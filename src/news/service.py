from typing import List
from jinja2 import Environment, FileSystemLoader
from lib.external.express import Express
from lib.infra.s3 import S3
from lib.external.gnews import GNews
from lib.langchain.openai import OpenAI
from datetime import datetime, timedelta
import json
from collections import defaultdict
from functools import lru_cache
from io import BytesIO
import logging
import os
import shutil
import tempfile


class NewsService:
    def __init__(self):
        self.openAI = OpenAI()
        self.gnews = GNews()
        self.s3 = S3()
        # Use absolute path for templates
        template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "template")
        logging.info(f"Loading templates from: {template_dir}")
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.express = Express()

    def _fetch_news(self, provider_id: str, tags: List[str], from_date: datetime) -> List[dict]:
        news_list = [news for tag in tags for news in self.gnews.get_news(
            tag, from_date) if news.get("maintext")]

        vector_db_path = self._get_vector_db_path(provider_id)

        db = self.openAI.load_vector_db(
            vector_db_path) if vector_db_path else None

        if db is None:
            db = self.openAI.create_vector_db()
            # Save the newly created vector DB if there isn't one
            self._save_vector_db(provider_id, db)

        unique_news_list = [
            news for news in news_list if not self.openAI.is_duplicate(db, news["maintext"])
        ]

        # Handle ISO8601 dates with 'Z' timezone indicator
        def parse_date(date_str):
            if date_str.endswith('Z'):
                date_str = date_str[:-1]  # Remove trailing 'Z'
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            
        unique_news_list.sort(key=lambda news: parse_date(news["date_publish"]))

        return unique_news_list

    @lru_cache(maxsize=10)
    def _get_vector_db_path(self, provider_id: str):
        try:
            # Get all files in the vector db directory
            vector_db_files = self.s3.get_files_from_dir(f"{provider_id}/collection/vectordb/")
            
            if not vector_db_files:
                logging.info(f"No vector database files found for provider {provider_id}")
                return None
                
            # Create a temporary directory to download the vector DB files
            import tempfile
            import os
            
            temp_dir = os.path.join(tempfile.gettempdir(), f"vectordb_{provider_id}")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Download all files to the temporary directory
            for file_key in vector_db_files:
                # Extract the filename from the key
                relative_path = file_key.replace(f"{provider_id}/collection/vectordb/", "")
                target_path = os.path.join(temp_dir, relative_path)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                
                # Download the file and copy to target path
                downloaded_path = self.s3.get_file(file_key)
                if downloaded_path:
                    # Copy to the structured directory
                    shutil.copy2(downloaded_path, target_path)
            
            logging.info(f"Downloaded vector database for provider {provider_id} to {temp_dir}")
            return temp_dir
        except Exception as e:
            logging.info(f"Vector database not found for provider {provider_id}, will create a new one: {str(e)}")
            return None

    def _save_vector_db(self, provider_id: str, db):
        """Save vector DB to S3"""
        try:
            # Save the vector DB locally
            local_dir = self.openAI.save_vector_db_local(db, "temp_vectordb")
            logging.info(f"Vector DB saved locally to {local_dir}")
            
            # Upload each file in the directory
            for root, _, files in os.walk(local_dir):
                for filename in files:
                    local_file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(local_file_path, local_dir)
                    s3_key = f"{provider_id}/collection/vectordb/{relative_path}"
                    
                    # Upload individual file
                    self.s3.upload_file(local_file_path, s3_key)
                    logging.info(f"Uploaded {local_file_path} to {s3_key}")
            
            logging.info(f"Successfully saved vector DB for provider {provider_id}")
        except Exception as e:
            logging.warning(f"Failed to save vector DB for provider {provider_id}: {e}")

    def daily_summarize(self, provider_id: str, locale: str, tags: List[str], dispatch_day: int):
        today = datetime.now()
        diff = dispatch_day - today.weekday()
        dispatch_date = today + timedelta(days=diff, weeks=-1)

        from_date = today - timedelta(days=2) \
            if today - dispatch_date > timedelta(days=2) \
            else dispatch_date

        unique_news_list = self._fetch_news(provider_id, tags, from_date)

        groups = defaultdict(list)
        for news in unique_news_list:
            # Handle ISO8601 dates with 'Z' timezone indicator
            date_str = news["date_publish"]
            if date_str.endswith('Z'):
                date_str = date_str[:-1]  # Remove trailing 'Z'
            date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S").date()
            groups[date].append(news)

        for date, news_list in groups.items():
            contents = [{"title": news["title"], "content": news["maintext"],
                         "url": news["url"]} for news in news_list]

            news_summarizer = f"""
            You are a professional news summarizer. Summarize the given articles into a single, engaging summary.
            ### **Instructions**:
            - **Language:** Write in {locale}.
            - **Title:** Create a catchy title.
            - **Content:** Combine all articles into a **single, coherent summary** (~100 words).
            - **Formatting:** Use semantic HTML:
              - `<p>` for paragraphs
              - `<ul>` / `<li>` for lists (if needed)
              - `<strong>` for **important facts**
              - `<em>` for *key phrases*
              - `<i>` for *quotes or foreign words*
            - **Emojis:** Use sparingly.
            - **Output:** Return a JSON with:
              - `"title"`: Summary title
              - `"content"`: Summary text (HTML formatted)
            """

            # Log the contents for debugging
            logging.info(f"Generating summary for {len(contents)} articles")
            
            # Pass contents directly instead of json-encoded string
            prompt = self.openAI.generate_prompt(news_summarizer, contents)
            response = self.openAI.send_request(prompt)

            json_obj = self.openAI.parse_json_result(response)

            json_obj["urls"] = [content["url"] for content in contents]
            # Convert date object to ISO format string for JSON serialization
            json_obj["date"] = date.isoformat()

            file_obj = self.s3.deserialize_json(json_obj)
            self.s3.upload_file_object(
                file_obj, f"{provider_id}/collection/{date}.json")

    def make_newsletter(self, provider_id: str, locale: str, tags: List[str]):
        intro_and_outro = f"""
        You are a creative newsletter writer. Write an engaging intro and outro for the newsletter.
        ### **Instructions**:
        - **Language:** Write in {locale}.
        - **Tone:** Friendly, engaging, and professional.
        - **Intro (~100 words):** Hook readers, set the context, preview the content.
        - **Outro (~100 words):** Wrap up smoothly, encourage readers to stay tuned.
        - **Keywords:** This newsletter is about {tags}.
        - **Formatting:** Use:
          - `<h2>` for section titles
          - `<p>` for paragraphs
          - `<strong>` for **highlights**
          - `<em>` for *subtle emphasis*
          - `<i>` for *quotes or foreign words*
        - **Emojis:** Use sparingly.
        - **Output:** Return a JSON with:
          - `"intro"`: Introduction text
          - `"outro"`: Conclusion text
        """

        files = self.s3.get_files_from_dir(f"{provider_id}/collection/")
        
        # Filter out non-JSON files (like vectordb files)
        json_files = [f for f in files if f.endswith('.json') and 'vectordb' not in f]
        
        # Sort the filtered files by date
        json_files.sort(key=lambda f: datetime.strptime(
            f.split("/")[-1].replace(".json", ""), "%Y-%m-%d"))

        contents = self.s3.serialize_json_files(json_files)
        prompt = self.openAI.generate_prompt(
            intro_and_outro, contents)
        response = self.openAI.send_request(prompt)
        result = self.openAI.parse_json_result(response)

        newsletter = {
            "title": f"{provider_id} Weekly Newsletter",
            "logo_url": "https://via.placeholder.com/200x50",
            "hero_title": "Stay Updated with the Latest News",
            "hero_text": "Here are the top stories of the week curated just for you!",
            "hero_button_url": "#",
            "hero_button_text": "Explore More",
            "articles": contents,
            "unsubscribe_url": "#",
            "preferences_url": "#",
            "company_name": "Infoscribe Inc.",
            "intro": result["intro"],
            "outro": result["outro"]
        }

        html = self._create_html_doc(newsletter)
        dispatch_date = datetime.today()
        html_bytes = html.encode("utf-8")
        file_obj = BytesIO(html_bytes)
        # Convert to string for file path
        dispatch_date_str = dispatch_date.strftime("%Y-%m-%d")
        self.s3.upload_file_object(
            file_obj, f"{provider_id}/newsletter/{dispatch_date_str}.html")
        self.express.dispatch_newsletter(
            provider_id, dispatch_date_str)

    def _create_html_doc(self, newsletter: dict) -> str:
        template = self.env.get_template("template.html")
        return template.render(newsletter)

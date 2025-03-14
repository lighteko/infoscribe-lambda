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


class NewsService:
    def __init__(self):
        self.openAI = OpenAI()
        self.gnews = GNews()
        self.s3 = S3()
        self.env = Environment(loader=FileSystemLoader("templates"))
        self.express = Express()

    def _fetch_news(self, provider_id: str, categories: List[str], from_date: datetime) -> List[dict]:
        news_list = [news for category in categories for news in self.gnews.get_news(
            category, from_date) if news.get("maintext")]

        vector_db_path = self._get_vector_db_path(provider_id)

        db = self.openAI.load_vector_db(
            vector_db_path) if vector_db_path else None

        if db is None:
            db = self.openAI.create_vector_db()

        unique_news_list = [
            news for news in news_list if not self.openAI.is_duplicate(db, news["maintext"])
        ]

        unique_news_list.sort(key=lambda news: datetime.strptime(
            news["date_publish"], "%Y-%m-%dT%H:%M:%S"))

        return unique_news_list

    @lru_cache(maxsize=10)
    def _get_vector_db_path(self, provider_id: str):
        return self.s3.get_file(path=f"{provider_id}/collection/vectordb/index")

    def daily_summarize(self, provider_id: str, locale: str, categories: List[str], dispatch_day: int):
        today = datetime.now()
        diff = dispatch_day - today.weekday()
        dispatch_date = today + timedelta(days=diff, weeks=-1)

        from_date = today - timedelta(days=2) \
            if today - dispatch_date > timedelta(days=2) \
            else dispatch_date

        unique_news_list = self._fetch_news(provider_id, categories, from_date)

        groups = defaultdict(list)
        for news in unique_news_list:
            date = datetime.strptime(
                news["date_publish"], "%Y-%m-%dT%H:%M:%S").date()
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

            prompt = self.openAI.generate_prompt(
                news_summarizer, json.dumps(contents, ensure_ascii=False))
            response = self.openAI.send_request(prompt)

            json_obj = self.openAI.parse_json_result(response)

            json_obj["urls"] = [content["url"] for content in contents]
            json_obj["date"] = date

            file_obj = self.s3.deserialize_json(json_obj)
            self.s3.upload_file_object(
                file_obj, f"{provider_id}/collection/{date}.json")

    def make_newsletter(self, provider_id: str, locale: str, categories: List[str]):
        intro_and_outro = f"""
        You are a creative newsletter writer. Write an engaging intro and outro for the newsletter.
        ### **Instructions**:
        - **Language:** Write in {locale}.
        - **Tone:** Friendly, engaging, and professional.
        - **Intro (~100 words):** Hook readers, set the context, preview the content.
        - **Outro (~100 words):** Wrap up smoothly, encourage readers to stay tuned.
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
        files.sort(key=lambda f: datetime.strptime(
            f.split("/")[-1].replace(".json", ""), "%Y-%m-%d"))

        contents = self.s3.serialize_json_files(files)
        prompt = self.openAI.generate_prompt(
            intro_and_outro, json.dumps(contents, ensure_ascii=False))
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
        self.s3.upload_file_object(
            file_obj, f"{provider_id}/newsletter/{dispatch_date}.html")
        self.express.dispatch_newsletter(
            provider_id, dispatch_date.strftime("%Y-%m-%d"))

    def _create_html_doc(self, newsletter: dict) -> str:
        template = self.env.get_template("template.html")
        return template.render(newsletter)

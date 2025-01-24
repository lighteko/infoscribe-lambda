from typing import List

from lib.news.gnews import GNews
from lib.llm.llm import LLM
import json


class NewsService:
    def __init__(self):
        self.llm = LLM()
        self.gnews = GNews()

    def make_newsletter(self, lang: str, country: str, keywords: List[str], level: str):
        news_list = []
        for keyword in keywords:
            news = self.gnews.get_news(lang, country, keyword)
            news_list.extend(news)
        contents = []
        for news in news_list:
            if news["maintext"] == None:
                continue
            news_summarizer = f"""
You are a skilled casual columnist to summarize the news articles I will provide.
You should follow these instructions:
1. Write the summary in {lang}. Try to make the title catchy. Please indicate the date of the event.
2. Try to use emojis.
3. Use <strong> tag to emphasize certain terms or sentences.
4. The audience is in {level} level.
5. Answer in JSON format, with two keys: "title", "content".
6. The content should be 100 words long.
"""
            prompt = self.llm.generate_prompt(news_summarizer,
                                              f"Title: {news["title"]} / News: {news["maintext"]} / Date: {news["date_publish"]}")
            result = self.llm.send_request(prompt)
            result = result.replace("```json", "").replace("```", "")
            result = json.loads(result)
            contents.append({
                "title": result["title"],
                "content": result["content"],
                "url": news["url"]
            })

        intro_and_outro = f"""
You are a skilled casual columnist to write an intro and outro for the newsletter about the contents I will provide.
You should follow these instructions:
1. Write both intro and outro in {lang}. Try to make them catchy, and use emojis.
2. The audience is in {level} level.
3. The name of our platform is Infoscribe.
4. Answer in JSON format, with two keys: "intro", "outro".
5. The content should be 100 words long each.
"""
        prompt = self.llm.generate_prompt(intro_and_outro, contents)
        result = self.llm.send_request(prompt)
        result = result.replace("```json", "").replace("```", "")
        result = json.loads(result)
        return {
            "intro": result["intro"],
            "content": contents,
            "outro": result["outro"]
        }

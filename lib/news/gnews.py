from flask import Flask
from newsplease import NewsPlease
import requests
import logging


class GNews:
    API_KEY: str = ""

    def __init__(self):
        pass

    @classmethod
    def init_app(cls, app: Flask):
        cls.API_KEY = app.config["GNEWS_API_KEY"]

    def get_news(self, topic: str):
        if GNews.API_KEY is "":
            logging.error("G News API KEY not initialized")
        response = requests.get(
            f"https://gnews.io/api/v4/search?q={topic}&lang=en&country=us&max=10&apikey={GNews.API_KEY}")
        news_list = []
        res = response.json()
        news_link_list = [article["url"]
                          for article in res["articles"]]
        for news in news_link_list:
            article = NewsPlease.from_url(news)
            try:
                data: dict = article.get_serializable_dict()
                news_list.append(data)
            except Exception as e:
                logging.error(f"Error processing article: {e}")

        return news_list

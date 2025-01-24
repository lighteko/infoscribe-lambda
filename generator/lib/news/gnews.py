from flask import Flask
from newsplease import NewsPlease
import requests
import datetime as dt
import logging


class GNews:
    API_KEY: str

    def __init__(self):
        pass

    @classmethod
    def init_app(cls, app: Flask):
        cls.API_KEY = app.config["GNEWS_API_KEY"]

    def get_news(self, lang, country, topic: str):
        response = requests.get(
            f"https://gnews.io/api/v4/search?q={topic}&lang={lang}&country={country}&max=10&apikey={GNews.API_KEY}")
        news_list = []
        news_link_list = [article["url"]
                          for article in response.json()["articles"]]
        for news in news_link_list:
            article = NewsPlease.from_url(news)
            try:
                data: dict = article.get_serializable_dict()
                date_download = dt.datetime.strptime(
                    data["date_download"], "%Y-%m-%d %H:%M:%S")
                date_published = dt.datetime.strptime(
                    data["date_publish"], "%Y-%m-%d %H:%M:%S")
                deltatime = date_download - date_published
                if deltatime.days > 7:
                    continue
                news_list.append(data)
            except Exception as e:
                logging.error(f"Error processing article: {e}")

        return news_list

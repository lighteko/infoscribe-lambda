import requests
import logging
from src.app import App


class Express:
    API_END_POINT: str = ""

    def __init__(self):
        pass

    @classmethod
    def init_app(cls, app: App):
        cls.API_END_POINT = app.config["EXPRESS_END_POINT"]

    def send_newsletter(self, newsletter: dict):
        pass

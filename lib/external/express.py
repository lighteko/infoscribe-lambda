from flask import Flask
import requests
import logging


class Express:
    API_END_POINT: str = ""

    def __init__(self):
        pass

    @classmethod
    def init_app(cls, app: Flask):
        cls.API_END_POINT = app.config["EXPRESS_END_POINT"]

    def send_newsletter(self, newsletter: dict):
        pass

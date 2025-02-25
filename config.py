import os
from os.path import join, dirname
from dotenv import load_dotenv
from src.app import App

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


class BaseConfig(object):
    # LOGGER
    LOGGING_PATH = '../logs'

    # LANGCHAIN
    LANGSMITH_TRACING = os.environ.get('LANGSMITH_TRACING', '')
    LANGSMITH_ENDPOINT = os.environ.get('LANGSMITH_ENDPOINT', '')
    LANGSMITH_API_KEY = os.environ.get('LANGSMITH_API_KEY', '')
    LANGSMITH_PROJECT = os.environ.get('LANGSMITH_PROJECT', '')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

    # GNEWS
    GNEWS_API_KEY = os.environ.get("GNEWS_API_KEY", '')

    def __init__(self, app: App):
        self.init_app(app)

    @classmethod
    def init_app(cls, app: App):
        app.config.from_object(cls)

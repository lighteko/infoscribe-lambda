import os
from os.path import join, dirname
from dotenv import load_dotenv
from typing import Any

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


class BaseConfig:
    # LOGGER
    LOGGING_PATH = '../logs'

    # AWS
    AWS_REGION = os.environ.get('AWS_REGION', '')
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY', '')
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY', '')
    AWS_BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME', '')

    # LANGCHAIN
    LANGSMITH_TRACING = os.environ.get('LANGSMITH_TRACING', '')
    LANGSMITH_ENDPOINT = os.environ.get('LANGSMITH_ENDPOINT', '')
    LANGSMITH_API_KEY = os.environ.get('LANGSMITH_API_KEY', '')
    LANGSMITH_PROJECT = os.environ.get('LANGSMITH_PROJECT', '')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

    # GNEWS
    GNEWS_API_KEY = os.environ.get("GNEWS_API_KEY", '')

    # EXPRESS
    EXPRESS_END_POINT = os.environ.get("EXPRESS_END_POINT", '')

    def __init__(self, app: Any):
        self.init_app(app)

    @classmethod
    def init_app(cls, app: Any):
        app.config.from_object(cls)

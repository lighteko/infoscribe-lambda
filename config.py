import os
from typing import Any
import logging


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
        # Log some key configuration values to verify they're loaded
        print("===== Environment Variables Loaded =====")
        print(f"AWS_REGION: {cls.AWS_REGION}")
        print(f"OPENAI_API_KEY set: {bool(cls.OPENAI_API_KEY)}")
        print(f"GNEWS_API_KEY set: {bool(cls.GNEWS_API_KEY)}")
        print(f"EXPRESS_END_POINT: {cls.EXPRESS_END_POINT}")
        print("=====================================")

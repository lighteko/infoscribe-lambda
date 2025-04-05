from src.news.collector import NewsCollector
from src.news.builder import NewsletterBuilder
from lib.external.express import Express
from lib.external.gnews import GNews
from lib.langchain.openai import OpenAI
from config import BaseConfig
from typing import Any, Dict
import logging
from src.models.events import LambdaEvent


class Config(dict):
    @classmethod
    def from_object(cls, obj: Any) -> 'Config':
        if not hasattr(obj, '__dict__'):
            raise ValueError("Object must have __dict__ attribute")

        config = cls()
        for key, value in obj.__dict__.items():
            config[key] = value
        return config


class App:
    def __init__(self):
        self.config = Config()
        self.collector = NewsCollector()
        self.builder = NewsletterBuilder()

    def handle(self, event: Dict[str, Any], context: Any):
        """
    Process EventBridge events for news collection and newsletter building

    Args:
        event: The event dict from AWS Lambda
        context: The context object from AWS Lambda
    """
        try:
            # Parse and validate the event
            parsed_event = LambdaEvent.model_validate(event)
            detail = parsed_event.detail

            # Process based on event type
            if detail.eventType == "collect":
                self.collector.collect(
                    detail.providerId,
                    detail.locale,
                    detail.tags,
                    detail.dispatchDay or 0
                )

            elif detail.eventType == "build":
                self.builder.build(
                    detail.providerId,
                    detail.locale,
                    detail.tags
                )

            else:
                logging.warning(f"Unsupported event type: {detail.eventType}")

        except Exception as e:
            logging.exception(f"Error processing event: {str(e)}")
            # Reraise to mark Lambda execution as failed
            raise


def create_app():
    app = App()

    BaseConfig(app)
    OpenAI.init_app(app)
    GNews.init_app(app)
    Express.init_app(app)

    return app

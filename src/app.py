from lib.external.express import Express
from lib.external.gnews import GNews
from lib.langchain.openai import OpenAI
from config import BaseConfig
from src.news.controller import Controller
from typing import Any


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
        self.news_controller = Controller()

    def handle(self, event):
        """
        Handle AWS EventBridge events
        """
        try:
            detail = event.get('detail', {})
            source = event.get('source')

            # Extract event type from detail 
            event_type = detail.get('eventType')
            if not event_type:
                raise ValueError("Event type is required in detail")

            # Process the event using the news controller
            response = self.news_controller.get(detail)

            return {
                'status_code': response.get('error', 200),
                'source': source,
                'result': response
            }

        except Exception as e:
            return {
                'status_code': 500,
                'error': str(e),
                'source': event.get('source')
            }


def create_app():
    app = App()

    BaseConfig(app)
    OpenAI.init_app(app)
    GNews.init_app(app)
    Express.init_app(app)

    return app

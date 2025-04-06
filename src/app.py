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
    def __init__(self):
        self.config = {}
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def from_object(self, obj):
        """Load configuration from an object's class attributes"""
        for key in dir(obj):
            if not key.startswith('__') and not callable(getattr(obj, key)):
                value = getattr(obj, key)
                self.config[key] = value
                print(f"Loaded config: {key}={value}")


class App:
    def __init__(self):
        self.config = Config()
        # Don't create service instances here

    def init_app(self):
        # Don't initialize services again - they're already initialized in create_app
        # Only create service instances
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
    import logging
    import os
    from dotenv import load_dotenv
    from pathlib import Path

    # Load environment variables from .env file with explicit path
    dotenv_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=dotenv_path)
    logging.info(f"LAMBDA DEBUG: Loading .env from {dotenv_path}")
    
    # Debug environment variables
    logging.info("LAMBDA DEBUG: Environment variables after loading:")
    logging.info(f"OPENAI_API_KEY set: {bool(os.environ.get('OPENAI_API_KEY'))}")
    logging.info(f"GNEWS_API_KEY set: {bool(os.environ.get('GNEWS_API_KEY'))}")
    logging.info(f"AWS_REGION set: {bool(os.environ.get('AWS_REGION'))}")
    
    logging.info("LAMBDA DEBUG: Starting create_app function")

    try:
        app = App()
        logging.info("LAMBDA DEBUG: App instance created")

        # Initialize all service classes first
        logging.info("LAMBDA DEBUG: Initializing BaseConfig")
        BaseConfig(app)
        logging.info("LAMBDA DEBUG: Initializing OpenAI")
        OpenAI.init_app(app)
        logging.info("LAMBDA DEBUG: Initializing GNews")
        GNews.init_app(app)
        logging.info("LAMBDA DEBUG: Initializing Express")
        Express.init_app(app)
        logging.info("LAMBDA DEBUG: Service classes initialized")

        # Only create service instances after initializing all services
        logging.info("LAMBDA DEBUG: Initializing service instances")
        app.init_app()
        logging.info("LAMBDA DEBUG: All services initialized")

        return app
    except Exception as e:
        logging.error(f"LAMBDA DEBUG: Error in create_app: {str(e)}")
        raise

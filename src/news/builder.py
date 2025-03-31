import logging
from typing import List
from src.news.service import NewsService


class NewsletterBuilder:
    """Handles newsletter building operations"""

    def __init__(self):
        self.service = NewsService()

    def build(self, provider_id: str, locale: str, tags: List[str]) -> None:
        """
        Build a newsletter for a provider

        Args:
            provider_id: The provider identifier
            locale: The locale for the newsletter
            tags: List of news keywords to include
        """
        logging.info(
            f"Building newsletter for provider: {provider_id}, tags: {tags}")

        try:
            self.service.make_newsletter(provider_id, locale, tags)
            logging.info(
                f"Successfully built newsletter for provider {provider_id}")
        except Exception as e:
            logging.exception(f"Failed to build newsletter: {str(e)}")
            raise

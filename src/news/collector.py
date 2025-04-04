import logging
from typing import List
from src.news.service import NewsService


class NewsCollector:
    """Handles news collection operations"""

    def __init__(self):
        self.service = NewsService()

    def collect(self, provider_id: str, locale: str, categories: List[str], dispatch_day: int = 0) -> None:
        """
        Collect and summarize daily news for a provider

        Args:
            provider_id: The provider identifier
            locale: The locale for news articles
            categories: List of news categories to collect
            dispatch_day: Day offset for dispatch
        """
        logging.info(
            f"Collecting news for provider: {provider_id}, categories: {categories}")

        try:
            self.service.daily_summarize(
                provider_id, locale, categories, dispatch_day)
            logging.info(
                f"Successfully collected news for provider {provider_id}")
        except Exception as e:
            logging.exception(f"Failed to collect news: {str(e)}")
            raise

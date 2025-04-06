from datetime import datetime
from typing import List, Any, Dict
from newsplease import NewsPlease
import requests
import logging


class GNews:
    API_KEY: str = ""

    def __init__(self):
        pass

    @classmethod
    def init_app(cls, app: Any):
        cls.API_KEY = app.config.get("GNEWS_API_KEY", "")
        if not cls.API_KEY:
            logging.warning("GNews API key not configured")

    def get_news(self, topic: str, from_date: datetime) -> List[Dict[str, Any]]:
        if not GNews.API_KEY:
            raise ValueError("GNews API key not initialized")
        
        try:
            response = requests.get(
                f"https://gnews.io/api/v4/search?q={topic}&from={from_date}&lang=en&country=us&max=10&apikey={GNews.API_KEY}"
            )
            response.raise_for_status()
            
            news_list = []
            res = response.json()
            
            if "articles" not in res:
                logging.warning(f"No articles found for topic: {topic}")
                return []
                
            news_link_list = [article["url"] for article in res["articles"]]
            
            for news_url in news_link_list:
                try:
                    article = NewsPlease.from_url(news_url)
                    if article is None:
                        logging.warning(f"Could not fetch article from {news_url}")
                        continue
                        
                    data = article.get_dict()
                    if not data:
                        logging.warning(f"No data extracted from article {news_url}")
                        continue
                        
                    news_list.append(data)
                except Exception as e:
                    logging.error(f"Error processing article {news_url}: {e}")
                    continue

            return news_list
            
        except requests.RequestException as e:
            logging.error(f"Error fetching news from GNews API: {e}")
            raise ValueError(f"Failed to fetch news: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in get_news: {e}")
            raise

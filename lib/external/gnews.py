from datetime import datetime
from typing import List, Any, Dict
import requests
import logging
from datetime import timezone
import os


class GNews:
    API_KEY: str = ""

    def __init__(self):
        pass

    @classmethod
    def init_app(cls, app: Any):
        print("LAMBDA DEBUG: Initializing GNews API key")
        cls.API_KEY = app.config.get("GNEWS_API_KEY", "")
        
        # Enhanced debugging
        if not cls.API_KEY:
            env_api_key = os.environ.get("GNEWS_API_KEY", "")
            if env_api_key:
                print(f"LAMBDA DEBUG: GNews API key found in environment but not in config")
                # Use the environment variable directly
                cls.API_KEY = env_api_key
                print("LAMBDA DEBUG: Using GNews API key from environment directly")
            else:
                print("GNews API key not configured in config or environment")
        else:
            print("LAMBDA DEBUG: GNews API key configured successfully")

    def get_news(self, topic: str, from_date: datetime) -> List[Dict[str, Any]]:
        print(f"LAMBDA DEBUG: Fetching news for topic: {topic}")
        if not GNews.API_KEY:
            print("LAMBDA DEBUG: GNews API key not initialized")
            raise ValueError("GNews API key not initialized")
        
        try:
            # Format date for GNews API
            from_date_str = from_date.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            print(f"LAMBDA DEBUG: Fetching news from date: {from_date_str}")
            
            response = requests.get(
                f"https://gnews.io/api/v4/search?q={topic}&from={from_date_str}&lang=en&country=us&max=10&apikey={GNews.API_KEY}"
            )
            response.raise_for_status()
            
            news_list = []
            res = response.json()
            
            if "articles" not in res:
                print(f"No articles found for topic: {topic}")
                return []
                
            print(f"LAMBDA DEBUG: Found {len(res['articles'])} articles for topic: {topic}")
                
            # Process articles directly from GNews API response
            for article in res["articles"]:
                try:
                    # Create a simplified article structure
                    processed_article = {
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "content": article.get("content", ""),
                        "maintext": article.get("content", ""),  # Use content as maintext
                        "url": article.get("url", ""),
                        "source": article.get("source", {}).get("name", ""),
                        "date_publish": article.get("publishedAt", "")
                    }
                    
                    # Only include articles with content
                    if processed_article["maintext"]:
                        news_list.append(processed_article)
                    
                except Exception as e:
                    print(f"Error processing article: {e}")
                    continue

            print(f"LAMBDA DEBUG: Successfully processed {len(news_list)} articles")
            return news_list
            
        except requests.RequestException as e:
            print(f"Error fetching news from GNews API: {e}")
            raise ValueError(f"Failed to fetch news: {str(e)}")
        except Exception as e:
            print(f"Unexpected error in get_news: {e}")
            raise

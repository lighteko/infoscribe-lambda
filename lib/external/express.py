import requests
import logging
from typing import Any


class Express:
    API_END_POINT: str = ""

    def __init__(self):
        if not Express.API_END_POINT:
            print("Express API endpoint not initialized")

    @classmethod
    def init_app(cls, app: Any) -> None:
        cls.API_END_POINT = app.config.get("EXPRESS_END_POINT", "")
        if not cls.API_END_POINT:
            print("Express API endpoint not configured")

    def dispatch_newsletter(self, provider_id: str, dispatch_date: str) -> bool:
        if not Express.API_END_POINT:
            raise ValueError("Express API endpoint not initialized")
            
        try:
            response = requests.post(
                f"{Express.API_END_POINT}/dispatch",
                json={
                    "providerId": provider_id,
                    "dispatchDate": dispatch_date
                }
            )
            response.raise_for_status()
            return True
            
        except requests.RequestException as e:
            print(f"Error dispatching newsletter: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error in dispatch_newsletter: {e}")
            return False

import json
from src.news.service import NewsService


class Controller:
    def __init__(self):
        self.service = NewsService()

    def get(self, event):
        try:
            if "detail" in event:
                message = event["detail"]
            else:
                raise Exception("Missing detail in event")

            event_type = message.get("eventType")

            provider_id = message.get("providerId")
            locale = message.get("locale")
            categories = message.get("categories")
            dispatch_day = message.get("dispatchDay")

            if not provider_id or not locale or not categories:
                raise Exception("Missing required fields: providerId, locale, or categories")

            if event_type == "collect":
                self.service.daily_summarize(
                    provider_id, locale, categories, dispatch_day)
            elif event_type == "build":
                self.service.make_newsletter(provider_id, locale, categories)
            else:
                raise Exception(f"Unsupported event type: {event_type}")

        except json.JSONDecodeError:
            raise Exception("Invalid JSON format in event")
        except KeyError as e:
            raise Exception(f"Missing key in event: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing event: {str(e)}")

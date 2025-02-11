import json
from src.news.service import NewsService
from src.make_output import make_output


class Controller:
    def __init__(self):
        self.service = NewsService()

    def get(self, event):
        try:
            if "detail" in event:
                message = event["detail"]
            else:
                return make_output(data={}, error=400, status="invalid event structure")

            event_type = message.get("eventType")

            if not event_type:
                return make_output(data={}, error=400, status="missing event type")

            provider_id = message.get("providerId")
            locale = message.get("locale")
            categories = message.get("categories")

            if not provider_id or not locale:
                return make_output(data={}, error=400, status="missing required fields")

            if event_type == "collect":
                self.service.daily_summarize(locale, categories)
            elif event_type == "build":
                self.service.make_newsletter(locale, categories)
            else:
                return make_output(data={}, error=400, status="invalid event type")

        except json.JSONDecodeError:
            return make_output(data={}, error=400, status="invalid JSON format")
        except KeyError:
            return make_output(data={}, error=400, status="missing necessary fields")
        except Exception as e:
            return make_output(data={}, error=500, status="internal server error", message=str(e))

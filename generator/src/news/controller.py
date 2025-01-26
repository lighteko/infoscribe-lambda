from flask.views import MethodView
from flask import request, abort
from src.news.service import NewsService
from src.make_output import make_output


class NewsController(MethodView):
    def __init__(self):
        self.service = NewsService()

    def get(self):
        lang = request.args.get("lang", default=None, type=str)
        country = request.args.get("country", default=None, type=str)
        level = request.args.get("level", default=None, type=str)
        keywords = request.args.get(
            "keywords", default=None, type=str)

        if lang == None or country == None or level == None or keywords == None:
            abort(400, description="Arguments are not fully provided")

        keywords = keywords.split(", ")

        response = self.service.make_newsletter(lang, country, keywords, level)

        return make_output(data=response)

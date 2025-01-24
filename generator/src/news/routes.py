from flask import Blueprint
from flask_restful import Api
from src.news.controller import NewsController

news_blueprint = Blueprint('news', __name__, url_prefix='/api/news')
news_api = Api(news_blueprint)

news_api.add_resource(NewsController, "/")


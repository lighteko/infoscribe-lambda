from flask import Flask, request, jsonify
from flask_cors import CORS
from lib.news.gnews import GNews
from lib.llm.llm import LLM

import logging
import json

from config import BaseConfig



def create_app():
    app = Flask(__name__)

    BaseConfig(app)
    LLM.init_app(app)
    GNews.init_app(app)
    CORS(app)
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
    register_blueprints(app)

    @app.route('/health')
    def health():
        resp = jsonify(health="healthy")
        resp.status_code = 200
        return resp

    app.logger.setLevel(logging.DEBUG)

    @app.before_request
    def log_request_info():
        app.logger.debug(f"Request Path: {request.path}")
        app.logger.debug(f"Request Method: {request.method}")
        app.logger.debug(f"Request Headers: {request.headers}")
        app.logger.debug(f"Request Data: {request.data}")

    # Define the after_request decorator to log response information
    @app.after_request
    def log_response_info(response):
        # Create a dictionary with the response information
        response_info = {
            'Status Code': response.status_code,
            'Headers': dict(response.headers),
            'Data': response.data.decode('utf-8')  # Assuming the response data is in UTF-8
        }

        # Decode the JSON data in the "Data" field
        try:
            decoded_data = json.loads(response_info['Data'])
        except json.JSONDecodeError as e:
            decoded_data = response_info['Data']

        # Include the decoded data in the log output
        log_output = f"Decoded Data:\n{decoded_data}"
        app.logger.debug(log_output)

        return response

    return app

def register_blueprints(app: Flask) -> None:
    from src.news.routes import news_api
    apis = [news_api]

    for _api in apis:
        app.register_blueprint(_api.blueprint)
from lib.external.express import Express
from lib.external.gnews import GNews
from lib.langchain.openai import OpenAI
from config import BaseConfig

class Config(dict):
    @classmethod
    def from_object(self, obj: object):
        assert isinstance(obj)
        members: dict = obj.__dict__()
        keys = members.keys()
        for key in keys:
            self[key] = members[key]

class App:
    def __init__(self):
        self.config = Config()

def create_app():
    app = App()

    BaseConfig(app)
    OpenAI.init_app(app)
    GNews.init_app(app)
    Express.init_app(app)

    return app

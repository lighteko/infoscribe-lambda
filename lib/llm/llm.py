import os
from flask import Flask
from langchain.callbacks import get_openai_callback
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate


class LLM:
    API_KEY = ""

    def __init__(self):
        self.llm = ChatOpenAI(api_key=LLM.API_KEY, model="gpt-4o-mini")

    @classmethod
    def init_app(cls, app: Flask):
        cls.API_KEY = app.config["OPENAI_API_KEY"]

    def send_request(self, messages):
        res = self.llm.invoke(messages)
        return res.content

    def generate_prompt(self, preset, data):
        messages = ChatPromptTemplate.from_messages([
            ("system", preset),
            ("ai", "Got it, here we go"),
            ("human", str(data).replace("{", "[").replace("}", "]"))
        ])
        prompt = messages.format_messages()

        return prompt

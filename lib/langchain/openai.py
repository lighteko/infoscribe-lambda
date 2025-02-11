import json
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
import numpy as np

from src.app import App


class OpenAI:
    API_KEY: str = ""

    def __init__(self):
        self.llm = ChatOpenAI(api_key=OpenAI.API_KEY, model="gpt-4o-mini")
        self.embeddings = OpenAIEmbeddings(
            api_key=OpenAI.API_KEY, model="text-embedding-3-large")

    @classmethod
    def init_app(cls, app: App):
        cls.API_KEY = app.config["OPENAI_API_KEY"]

    def send_request(self, messages):
        res = self.llm.invoke(messages)
        return res.content

    def generate_prompt(self, preset: str, data: dict):
        messages = ChatPromptTemplate.from_messages([
            ("system", preset),
            ("ai", "Got it, here we go"),
            ("human", json.dumps(data, ensure_ascii=False))
        ])
        return messages.format_messages()

    def is_duplicate(self, vector_db: FAISS, content: str, threshold: float = 0.85) -> bool:
        if not vector_db:
            raise ValueError("Vector DB was not provided")

        query_embedding = self.embeddings.embed_query(content)
        similar_docs = vector_db.similarity_search_by_vector(
            query_embedding, k=1)

        if similar_docs:
            existing_doc = similar_docs[0].page_content
            existing_embedding = self.embeddings.embed_query(existing_doc)
            similarity_score = self._calculate_cosine_similarity(
                query_embedding, existing_embedding)

            return similarity_score >= threshold

        return False

    def create_vector_db(self) -> FAISS:
        return FAISS.from_documents([], self.embeddings)

    def update_vector_db(self, vector_db: FAISS, content: str):

        if not vector_db:
            raise ValueError("Vector DB was not provided")

        try:
            document = Document(page_content=content)
            vector_db.add_documents([document])
        except Exception as e:
            print(f"Error occurred while updating vector db: {e}")

    def save_vector_db_local(self, vector_db: FAISS, name: str) -> str:
        path = os.path.join("/tmp", f"{name}")
        vector_db.save_local(path)
        return path

    @staticmethod
    def _calculate_cosine_similarity(vec1, vec2):
        vec1, vec2 = np.array(vec1), np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

import json
import os
import logging
from typing import List, Optional, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.schema import BaseMessage

import numpy as np
from io import BytesIO

from pydantic import SecretStr


class OpenAI:
    API_KEY: str = ""

    def __init__(self):
        logging.info("LAMBDA DEBUG: Initializing OpenAI instance")
        if not OpenAI.API_KEY:
            logging.error("LAMBDA DEBUG: OpenAI API key not initialized")
            raise ValueError("OpenAI API key not initialized")

        logging.info("LAMBDA DEBUG: Creating ChatOpenAI instance")
        self.llm = ChatOpenAI(
            api_key=SecretStr(OpenAI.API_KEY),
            model="gpt-4-turbo-preview",
            temperature=0.7
        )
        
        logging.info("LAMBDA DEBUG: Creating OpenAIEmbeddings instance")
        self.embeddings = OpenAIEmbeddings(
            api_key=OpenAI.API_KEY,
            model="text-embedding-3-large"
        )
        logging.info("LAMBDA DEBUG: OpenAI instance initialized successfully")

    @classmethod
    def init_app(cls, app: Any) -> None:
        logging.info("LAMBDA DEBUG: Setting up OpenAI API key from config")
        cls.API_KEY = app.config.get("OPENAI_API_KEY", "")
        if not cls.API_KEY:
            logging.warning("LAMBDA DEBUG: OpenAI API key not configured")
        else:
            logging.info("LAMBDA DEBUG: OpenAI API key configured successfully")

    def send_request(self, messages: List[BaseMessage]) -> str:
        try:
            res = self.llm.invoke(messages)
            if isinstance(res.content, str):
                return res.content
            raise ValueError("Unexpected response format from OpenAI")
        except Exception as e:
            logging.error(f"Error in OpenAI request: {e}")
            raise

    def parse_json_result(self, response: str) -> dict:
        try:
            # Remove code block markers if present
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = "\n".join(clean_response.split("\n")[1:-1])

            result = json.loads(clean_response)
            return result
        except json.JSONDecodeError as e:
            logging.error(f"JSON parsing error: {e}")
            raise ValueError(
                "The response was not properly formatted in JSON.")
        except Exception as e:
            logging.error(f"Unexpected error parsing JSON: {e}")
            raise

    def generate_prompt(self, preset: str, data: str) -> List[BaseMessage]:
        try:
            messages = ChatPromptTemplate.from_messages([
                ("system", preset),
                ("ai", "Got it, here we go"),
                ("human", json.dumps(data, ensure_ascii=False))
            ])
            return messages.format_messages()
        except Exception as e:
            logging.error(f"Error generating prompt: {e}")
            raise

    def is_duplicate(self, vector_db: FAISS, content: str, threshold: float = 0.85) -> bool:
        try:
            query_embedding = self.embeddings.embed_query(content)
            similar_docs = vector_db.similarity_search_by_vector(
                query_embedding, k=1)

            if similar_docs:
                existing_doc = similar_docs[0].page_content
                existing_embedding = self.embeddings.embed_query(existing_doc)
                similarity_score = self._calculate_cosine_similarity(
                    np.array(query_embedding), np.array(existing_embedding))
                if similarity_score >= threshold:
                    self.update_vector_db(vector_db, content)
                    return True
            return False
        except Exception as e:
            logging.error(f"Error checking for duplicates: {e}")
            raise

    def load_vector_db(self, path: str) -> Optional[FAISS]:
        try:
            return FAISS.load_local(path, self.embeddings)
        except Exception as e:
            logging.error(f"Error loading vector DB from {path}: {e}")
            raise

    def create_vector_db(self) -> FAISS:
        try:
            return FAISS.from_documents([], self.embeddings)
        except Exception as e:
            logging.error(f"Error creating vector DB: {e}")
            raise

    def update_vector_db(self, vector_db: FAISS, content: str) -> None:
        try:
            document = Document(page_content=content)
            vector_db.add_documents([document])
        except Exception as e:
            logging.error(f"Error updating vector DB: {e}")
            raise

    def save_vector_db_local(self, vector_db: FAISS, name: str) -> str:
        try:
            path = os.path.join("/tmp", name)
            vector_db.save_local(path)
            return path
        except Exception as e:
            logging.error(f"Error saving vector DB to {name}: {e}")
            raise

    @staticmethod
    def _calculate_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        try:
            return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
        except Exception as e:
            logging.error(f"Error calculating cosine similarity: {e}")
            raise

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
        print("LAMBDA DEBUG: Initializing OpenAI instance")
        if not OpenAI.API_KEY:
            print("LAMBDA DEBUG: OpenAI API key not initialized")
            raise ValueError("OpenAI API key not initialized")

        print("LAMBDA DEBUG: Creating ChatOpenAI instance")
        self.llm = ChatOpenAI(
            api_key=SecretStr(OpenAI.API_KEY),
            model="gpt-4-turbo-preview",
            temperature=0.7
        )
        
        print("LAMBDA DEBUG: Creating OpenAIEmbeddings instance")
        self.embeddings = OpenAIEmbeddings(
            api_key=OpenAI.API_KEY,
            model="text-embedding-3-large"
        )
        print("LAMBDA DEBUG: OpenAI instance initialized successfully")

    @classmethod
    def init_app(cls, app: Any) -> None:
        print("LAMBDA DEBUG: Setting up OpenAI API key from config")
        cls.API_KEY = app.config.get("OPENAI_API_KEY", "")
        
        # Enhanced debugging
        if not cls.API_KEY:
            import os
            env_api_key = os.environ.get("OPENAI_API_KEY", "")
            if env_api_key:
                print(f"LAMBDA DEBUG: OpenAI API key found in environment but not in config")
                # Use the environment variable directly
                cls.API_KEY = env_api_key
                print("LAMBDA DEBUG: Using OpenAI API key from environment directly")
            else:
                print("LAMBDA DEBUG: OpenAI API key not configured in config or environment")
        else:
            print("LAMBDA DEBUG: OpenAI API key configured successfully from config")

    def send_request(self, messages: List[BaseMessage]) -> str:
        try:
            res = self.llm.invoke(messages)
            if isinstance(res.content, str):
                return res.content
            raise ValueError("Unexpected response format from OpenAI")
        except Exception as e:
            print(f"Error in OpenAI request: {e}")
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
            print(f"JSON parsing error: {e}")
            raise ValueError(
                "The response was not properly formatted in JSON.")
        except Exception as e:
            print(f"Unexpected error parsing JSON: {e}")
            raise

    def generate_prompt(self, preset: str, data: Any) -> List[BaseMessage]:
        try:
            print(f"LAMBDA DEBUG: Generating prompt with data type: {type(data)}")
            
            # Convert data to a JSON string if it's not already a string
            if not isinstance(data, str):
                human_message = json.dumps(data, ensure_ascii=False)
            else:
                human_message = data
                
            # IMPORTANT: Escape braces to prevent LangChain from treating JSON as template
            # Double each { and } to escape them in string.format()
            human_message = human_message.replace("{", "{{").replace("}", "}}")
            print(f"LAMBDA DEBUG: Escaped JSON braces to prevent template substitution")
            
            # Create prompt template
            messages = ChatPromptTemplate.from_messages([
                ("system", preset),
                ("ai", "Got it, here we go"),
                ("human", human_message)
            ])
            
            # For debugging
            formatted_messages = messages.format_messages()
            print(f"LAMBDA DEBUG: Formatted {len(formatted_messages)} messages")
            
            return formatted_messages
        except Exception as e:
            print(f"Error generating prompt: {e}")
            print(f"Data causing error: {str(data)[:100]}...")  # Log first 100 chars
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
            print(f"Error checking for duplicates: {e}")
            raise

    def load_vector_db(self, path: str) -> Optional[FAISS]:
        try:
            return FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
        except Exception as e:
            print(f"Error loading vector DB from {path}: {e}")
            raise

    def create_vector_db(self) -> FAISS:
        try:
            # Get embedding dimension by creating a sample embedding
            sample_text = "This is a sample text to determine embedding dimension"
            sample_embedding = self.embeddings.embed_query(sample_text)
            dimension = len(sample_embedding)
            
            # Create an empty FAISS index with the correct dimension
            import faiss
            from langchain_community.docstore.in_memory import InMemoryDocstore
            
            index = faiss.IndexFlatL2(dimension)
            
            # Initialize with empty docstore and index_to_docstore_id
            return FAISS(
                embedding_function=self.embeddings,
                index=index,
                docstore=InMemoryDocstore({}),
                index_to_docstore_id={},
            )
        except Exception as e:
            print(f"Error creating vector DB: {e}")
            raise

    def update_vector_db(self, vector_db: FAISS, content: str) -> None:
        try:
            document = Document(page_content=content)
            vector_db.add_documents([document])
        except Exception as e:
            print(f"Error updating vector DB: {e}")
            raise

    def save_vector_db_local(self, vector_db: FAISS, name: str) -> str:
        try:
            path = os.path.join("/tmp", name)
            vector_db.save_local(path)
            return path
        except Exception as e:
            print(f"Error saving vector DB to {name}: {e}")
            raise

    @staticmethod
    def _calculate_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        try:
            return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
        except Exception as e:
            print(f"Error calculating cosine similarity: {e}")
            raise

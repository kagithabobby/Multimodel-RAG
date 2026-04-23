import os
import google.generativeai as genai
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
TEXT_EMBEDDING_MODEL = os.getenv("TEXT_EMBEDDING_MODEL", "models/text-embedding-004")
VLM_MODEL_NAME = os.getenv("VLM_MODEL_NAME", "gemini-1.5-flash")
COLLECTION_NAME = "bilingual_sensei"

class Retriever:
    def __init__(self):
        self.qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self.model = genai.GenerativeModel(VLM_MODEL_NAME)

    def _get_embedding(self, text: str) -> list[float]:
        result = genai.embed_content(
            model=TEXT_EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_query"
        )
        return result['embedding']

    def query(self, user_question: str) -> dict:
        """
        Performs a hybrid search and generates an English response.
        """
        query_vector = self._get_embedding(user_question)

        # Search Text Vectors
        text_results = self.qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=("text_vector", query_vector),
            limit=3
        )

        # Search Visual Context Vectors
        visual_results = self.qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=("visual_context_vector", query_vector),
            limit=3
        )

        # Build context
        context_parts = []
        sources = []

        for res in text_results:
            p = res.payload
            context_parts.append(f"[Text - Page {p.get('page_number')}]: {p.get('masked_text')}")
            sources.append({
                "type": "text",
                "page_number": p.get("page_number"),
                "score": res.score
            })

        for res in visual_results:
            p = res.payload
            context_parts.append(f"[Diagram - Page {p.get('page_number')}]: {p.get('english_summary')}")
            sources.append({
                "type": "image",
                "page_number": p.get("page_number"),
                "bbox": p.get("bbox"),
                "score": res.score
            })

        context_str = "\n\n".join(context_parts)

        # Generate final response
        prompt = f"""
You are "Bilingual Technical Sensei", an expert assistant.
Answer the user's English question using the provided context (which includes Japanese text summaries and diagram descriptions).
You must cite your sources by indicating the Page Number and type (Text or Diagram).
If you cannot find the answer in the context, say so gracefully.

Context:
{context_str}

User Question: {user_question}

Answer in English:
"""
        response = self.model.generate_content(prompt)

        return {
            "answer": response.text,
            "sources": sources
        }

retriever = Retriever()

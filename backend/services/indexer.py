import os
import uuid
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from dotenv import load_dotenv

from .pii_scraper import pii_scraper
from .vlm_service import vlm_service
from .pdf_processor import pdf_processor

load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
TEXT_EMBEDDING_MODEL = os.getenv("TEXT_EMBEDDING_MODEL", "models/text-embedding-004")
COLLECTION_NAME = "bilingual_sensei"

class Indexer:
    def __init__(self):
        self.qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        # Using Gemini text embedding model
        # genai is already configured in vlm_service or we assume GEMINI_API_KEY is in env
        
    def _get_embedding(self, text: str) -> list[float]:
        if not text.strip():
            return [0.0] * 768
            
        result = genai.embed_content(
            model=TEXT_EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']

    def ingest_pdf(self, pdf_path: str):
        print(f"Processing PDF: {pdf_path}")
        pages_data = pdf_processor.process_pdf(pdf_path)
        
        points_to_upsert = []
        
        for page in pages_data:
            page_num = page["page_number"]
            raw_text = page["text"]
            
            # 1. PII Scrubbing
            masked_text = pii_scraper.mask_text(raw_text)
            
            # 2. Text Vector (if text is not empty)
            if masked_text.strip():
                text_emb = self._get_embedding(masked_text)
                
                point_id = str(uuid.uuid4())
                points_to_upsert.append(
                    PointStruct(
                        id=point_id,
                        vector={
                            "text_vector": text_emb
                        },
                        payload={
                            "type": "text",
                            "page_number": page_num,
                            "raw_japanese_text": raw_text,
                            "masked_text": masked_text,
                            "source": pdf_path
                        }
                    )
                )
            
            # 3. Visual Context Vectors (Images/Diagrams)
            for img_info in page["images"]:
                img_path = img_info["path"]
                bbox = img_info["bbox"]
                
                # Get English summary from VLM
                summary = vlm_service.generate_diagram_summary(img_path)
                
                if summary.strip():
                    visual_emb = self._get_embedding(summary)
                    
                    img_point_id = str(uuid.uuid4())
                    points_to_upsert.append(
                        PointStruct(
                            id=img_point_id,
                            vector={
                                "visual_context_vector": visual_emb
                            },
                            payload={
                                "type": "image",
                                "page_number": page_num,
                                "image_path": img_path,
                                "bbox": bbox,
                                "english_summary": summary,
                                "source": pdf_path
                            }
                        )
                    )
                    
        # Upsert points into Qdrant
        if points_to_upsert:
            print(f"Upserting {len(points_to_upsert)} points into Qdrant...")
            self.qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=points_to_upsert
            )
            print("Upsert complete.")
        else:
            print("No valid data found to index.")

indexer = Indexer()

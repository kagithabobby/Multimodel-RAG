import os
import sys
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", 768))

COLLECTION_NAME = "bilingual_sensei"

def init_qdrant():
    print(f"Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}...")
    try:
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        # Check if collection exists
        if client.collection_exists(collection_name=COLLECTION_NAME):
            print(f"Collection '{COLLECTION_NAME}' already exists.")
            return

        print(f"Creating collection '{COLLECTION_NAME}' with multiple vectors...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                "text_vector": VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE
                ),
                "visual_context_vector": VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            }
        )
        print(f"Successfully initialized Qdrant collection '{COLLECTION_NAME}'.")
        
    except Exception as e:
        print(f"Error initializing Qdrant: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_qdrant()

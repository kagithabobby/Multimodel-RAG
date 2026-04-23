import os
import google.generativeai as genai
import redis
import hashlib
import json
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Use a default fallback model in case of None
VLM_MODEL_NAME = os.environ.get("VLM_MODEL_NAME", "gemini-1.5-flash")

# Setup Redis Cache
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

class VLMService:
    def __init__(self):
        self.model = genai.GenerativeModel(VLM_MODEL_NAME)
        try:
            self.cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
            # Test connection
            self.cache.ping()
            self.use_cache = True
        except redis.ConnectionError:
            print("Warning: Could not connect to Redis. Running without caching.")
            self.use_cache = False

    def generate_diagram_summary(self, image_path: str) -> str:
        """
        Analyzes the image and returns a technical English summary.
        """
        # Cache key based on image file content hash to ensure uniqueness
        file_hash = self._compute_file_hash(image_path)
        cache_key = f"vlm_summary:{file_hash}"
        
        if self.use_cache:
            cached_summary = self.cache.get(cache_key)
            if cached_summary:
                return cached_summary

        prompt = (
            "Identify all Japanese technical labels (Kanji/Katakana) in this diagram, "
            "explain the data flow, and generate a technical English summary."
        )

        try:
            # Upload the file to Gemini using File API (Recommended for 1.5)
            # Alternatively, we can pass image bytes or Pillow Image
            import PIL.Image
            img = PIL.Image.open(image_path)
            
            response = self.model.generate_content([prompt, img])
            summary = response.text
            
            if self.use_cache:
                self.cache.set(cache_key, summary)
                
            return summary
        except Exception as e:
            print(f"Error in VLM Service for image {image_path}: {e}")
            return "Failed to generate visual summary."

    def _compute_file_hash(self, file_path: str) -> str:
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                buf = f.read()
                hasher.update(buf)
            return hasher.hexdigest()
        except FileNotFoundError:
            return "unknown"

vlm_service = VLMService()

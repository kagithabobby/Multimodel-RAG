# Bilingual Technical Sensei Architecture

## System Overview

Bilingual Technical Sensei is a production-grade Multimodal RAG system that ingests Japanese technical PDFs and answers queries in English, citing side-by-side diagrams and text.

## High-Level Data Flow

1. **Ingestion Layer (PDF Processing)**
   - PyMuPDF extracts raw text and detects/crops diagrams from uploaded PDFs.
   - The PII Scraper masks sensitive information (Japanese names, IPs, My Number, Zaikyu Card, Japanese phone numbers) in the extracted text.
   - The Gemini 1.5 VLM analyzes cropped diagrams, generating technical English summaries. Redis caches these summaries to reduce API costs.

2. **Vector Storage Layer (Qdrant)**
   - Text chunks and VLM diagram summaries are embedded using Google's `text-embedding-004` (768 dimensions).
   - Qdrant stores two distinct named vectors:
     - `text_vector`: Embeddings for the Japanese text snippets.
     - `visual_context_vector`: Embeddings for the English VLM-generated descriptions.
   - Rich payloads are stored with each vector: `page_number`, `image_path`, `raw_japanese_text`, and `bbox`.

3. **Reasoning & Retrieval Layer (FastAPI + LlamaIndex)**
   - Users ask questions in English.
   - LlamaIndex performs a Hybrid Search across both the `text_vector` and the `visual_context_vector`.
   - An LLM Reranker evaluates results for cross-lingual relevance and builds the context.
   - Gemini generates the final English response, heavily citing the source diagrams and text.

4. **Presentation Layer (React + Vite)**
   - Dual-pane layout.
   - Left Pane: PDF.js rendered interactive document view.
   - Right Pane: AI chat interface streaming responses via WebSockets.
   - Interaction: Clicking source tags in the chat highlights the corresponding text or diagram in the PDF viewer using the stored `bbox` and `page_number`.

## Infrastructure

- **Docker Compose**: Orchestrates all services.
- **FastAPI**: Backend logic.
- **Qdrant**: Vector DB.
- **Redis**: Caching layer.
- **React Frontend**: User interface.

# Prerequisite & Course Planning Assistant

An RAG-based academic course planning assistant grounded in MIT OpenCourseWare catalog documents.

Built for Purple Merit Technologies AI/ML Engineer Intern Assessment - March 2026.

## Setup

### 1. Clone the repo
git clone <your-repo-url>
cd rag-simple

### 2. Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

### 3. Install dependencies
pip install groq faiss-cpu sentence-transformers streamlit requests beautifulsoup4 python-dotenv numpy

### 4. Add your Groq API key
Create a `.env` file:
GROQ_API_KEY=your_key_here

### 5. Build the index
python rag.py

### 6. Run the app
streamlit run app.py

### 7. Run evaluation
python eval.py

## Architecture

- **Scraping**: BeautifulSoup scrapes 20 MIT OCW course pages
- **Chunking**: 600-word chunks with 100-word overlap
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (local)
- **Vector Store**: FAISS with cosine similarity (IndexFlatIP)
- **Retriever**: Top-6 chunks per query
- **LLM**: Groq Llama-3.3-70b-versatile
- **UI**: Streamlit chat interface

## Evaluation Results

| Metric | Score |
|---|---|
| Citation coverage | 25/25 (100%) |
| Prereq correctness | 5/10 (50%) |
| Abstention accuracy | 5/5 (100%) |

## Sources

All data sourced from MIT OpenCourseWare (ocw.mit.edu), accessed March 2026.
Covers 19 courses across algorithms, AI/ML, systems, mathematics, and security.

## Files

- `rag.py` — scraping, indexing, retrieval, LLM call
- `app.py` — Streamlit chat UI
- `eval.py` — 25-query evaluation set
- `index.faiss` — FAISS vector index
- `chunks.json` — chunked text + source URLs
# RAG Chat Application

A local Retrieval-Augmented Generation (RAG) chatbot with PyTorch documentation search, powered by Qwen2.5-Coder LLM.  
This setup is designed for searching through local codebases. The example on GitHub uses parsed PyTorch docstrings for demonstration, but you can adapt it to index and search your own project documentation or codebase.  

## Features

- **General Chat** - Code-trained LLM for programming questions
- **PyTorch RAG Chat** - Context-aware responses using PyTorch docstrings
- **Local Processing** - All inference runs on your machine
- **Redis Queue** - Async request handling between Streamlit and LLM worker (via Docker)


## Tech Stack

- **Frontend**: Streamlit (multi-page app)
- **LLM**: Qwen2.5-Coder-1.5B-Instruct
- **Embeddings**: sentence-transformers (all-mpnet-base-v2)
- **Queue**: Redis (Docker container)
- **Inference**: PyTorch + Transformers

## Quick Start

### Local Setup

```bash
# Start Redis
docker run -d -p 6379:6379 --name rag-redis redis:7-alpine

# Start LLM worker (requires GPU)
python app/llm_worker.py

# Start Streamlit
streamlit run app/front_st/pages/home_page.py
```


## Environment Variables

- `REDIS_URL` - Redis connection string (default: `redis://localhost:6379/0`)

## Requirements

- Python 3.10+
- CUDA-capable GPU (for LLM inference)
- 4GB+ VRAM
- Docker (for Redis container)

## How RAG parrt Works (in this case Pytorch docstrings)

1. User query → embedded with sentence-transformers
2. Find top-5 similar PyTorch docstrings via L2 distance
3. Augment query with relevant docs
4. Send to LLM for context-aware response
# Agentic RAG Assistant Architecture

```text
                ┌──────────────────┐
                │   User Query     │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Streamlit UI     │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ FastAPI Backend  │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Router Agent     │
                │ classify_intent  │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ FAISS Retriever  │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Gemini LLM       │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Grounded Answer  │
                │ + Citations      │
                └──────────────────┘
```
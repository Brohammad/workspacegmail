# ZenithSteel ZenBot - Gemini + LangSmith case study

This repository contains a self-contained example of a RAG-style chatbot (ZenBot)
that uses Google Gemini (gemini-1.5-flash) as the LLM and LangSmith for tracing.

What this implements
- Simulated knowledge base with CURRENT and OUTDATED documents.
- Two retrieval modes: `buggy` (returns outdated docs) and `fixed` (returns current docs).
- A prompt template that requires the model to only use retrieved documents, cite standards,
  include dates for pricing, and admit when information is unavailable.
- Sends traces to LangSmith using the LangChain `LangsmithTracer` callback (if compatible
  package versions are installed). Also writes local JSON traces under `langsmith_traces/`.

Files
- `.env` - contains LangSmith API key and project name, and a placeholder for GEMINI_API_KEY.
- `requirements.txt` - Python dependencies to install.
- `zenbot.py` - main script that runs the test queries for both buggy and fixed versions.

Setup
1. Create a virtual environment and activate it.

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Edit `.env` and set `GEMINI_API_KEY` to your Google Gemini API key. The `LANGSMITH_API_KEY`
   is already included (as provided); change it if you want to use your own.

Running

```bash
source .venv/bin/activate
python zenbot.py
```

Notes and caveats
- Library APIs for LangChain and the langchain-google-genai wrapper change often. If you
  get import errors or type errors, try adjusting package versions from `requirements.txt`.
- The script attempts to use `LangsmithTracer` (LangChain callback). If your installed
  version of LangChain/langsmith uses a different tracer class or requires different
  environment variables, consult the LangSmith docs and adapt the tracer instantiation.
- This example uses a simple deterministic retrieval function for clarity instead of a
  vector database. Replace `retrieve_documents()` with an embeddings + vector store
  retrieval (e.g., Chroma, Pinecone) for production.

What I tested
- The script is self-contained and simulates documents. It writes traces to `langsmith_traces/`.
  If tracer is active and configured correctly, runs will appear in the LangSmith project
  specified by `LANGSMITH_PROJECT`.

If you want, I can:
- Adjust the script to use an embeddings-based retriever (Chroma) and demonstrate true RAG.
- Add unit tests for the retrieval function and prompt generation.

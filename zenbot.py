"""ZenithSteel ZenBot case study

This script implements a retrieval-augmented ZenBot using Google Gemini (gemini-1.5-flash)
and LangSmith tracing. It simulates a knowledge base with CURRENT and OUTDATED documents.

Requirements:
 - Set GEMINI_API_KEY in the .env file.
 - LANGSMITH_API_KEY and LANGSMITH_PROJECT are read from .env (the provided value will be used).

Notes about libraries and versions: the code uses the 'langchain-google-genai' and
LangChain callback tracer for LangSmith. Library APIs change often; if you see errors
about missing symbols, upgrade/downgrade to versions compatible with your environment
as mentioned in README.md.
"""
from __future__ import annotations

import os
import json
from typing import List, Dict

from dotenv import load_dotenv

# LangChain & LangSmith imports
try:
    # LLM integration for Gemini via langchain-google-genai
    # Use ChatGoogleGenerativeAI (provided by langchain_google_genai) as the chat model
    from langchain_google_genai import ChatGoogleGenerativeAI
    # Use langchain_core tracer (installed as `langchain_core`) to send traces to LangSmith
    # LangChain Core exposes tracers under `langchain_core.tracers.langchain`
    from langchain_core.tracers.langchain import LangChainTracer
except Exception:
    # We import inside try/except so the user can read the script even if packages
    # are not yet installed. Running the script requires installing the requirements.
    GoogleGemini = None
    LangChainTracer = None


def build_documents() -> Dict[str, List[Dict]]:
    """Return simulated knowledge base documents.

    Each document is a dict with: id, title, text, metadata (source, date)
    """
    current_docs = [
        {
            "id": "fe550d_16mm_spec_current",
            "title": "Fe 550D 16mm specifications",
            "text": (
                "Yield Strength: 565 N/mm² (per IS 1786:2008)."
            ),
            "metadata": {"source": "spec_sheet_2024_current.pdf", "date": "2024-11-01"},
        },
        {
            "id": "tmt_12mm_price_current",
            "title": "TMT 12mm pricing",
            "text": "Price: ₹52,500 per MT.",
            "metadata": {"source": "pricing_november_2024.pdf", "date": "2024-11-15"},
        },
    ]

    outdated_docs = [
        {
            "id": "fe550d_16mm_spec_old",
            "title": "Fe 550D old spec",
            "text": "Yield Strength: 550 N/mm².",
            "metadata": {"source": "old_spec_2019.pdf", "date": "2019-03-15"},
        },
        {
            "id": "tmt_12mm_price_old",
            "title": "TMT 12mm old pricing",
            "text": "Price: ₹48,000 per MT.",
            "metadata": {"source": "pricing_Q2_2024.pdf", "date": "2024-06-01"},
        },
    ]

    return {"current": current_docs, "outdated": outdated_docs}


def retrieve_documents(version: str, query: str) -> List[Dict]:
    """Simple retrieval function.

    - version: 'buggy' returns outdated documents
               'fixed' returns current documents
    - query: used for relevance matching (simple keyword checks here)

    In a production RAG, swap this for an embeddings + vector store retrieval.
    """
    kb = build_documents()
    version_key = "outdated" if version == "buggy" else "current"
    docs = kb[version_key]

    # Very simple relevance: if query mentions 'yield' or 'Fe', return spec doc,
    # if mentions 'price' or 'TMT', return pricing doc.
    q = query.lower()
    retrieved: List[Dict] = []
    if any(k in q for k in ["yield", "fe", "550d"]):
        # pick spec doc
        for d in docs:
            if "spec" in d["id"] or "fe550d" in d["id"]:
                retrieved.append(d)

    if any(k in q for k in ["price", "tmt", "per mt", "price:"]):
        for d in docs:
            if "price" in d["id"] or "tmt" in d["id"]:
                retrieved.append(d)

    # If nothing matched but query is about delivery, we intentionally return empty
    # to ensure the bot says it doesn't have the info.
    return retrieved


def build_prompt(question: str, docs: List[Dict]) -> str:
    """Create a single string prompt that includes retrieved documents and strict instructions.

    We keep the prompt simple: system instructions followed by enumerated doc contents
    and the user question.
    """
    system_instructions = (
        "You are ZenithSteel ZenBot. Answer only using the information explicitly provided in the\n"
        "retrieved documents below. Do not hallucinate. For specifications, cite the standard.\n"
        "For prices, include the document date. If information isn't available in the retrieved\n"
        "documents, admit you don't have it. Provide short, factual answers and include the\n"
        "document source and date for each factual claim."
    )

    docs_text = "\n\n".join(
        [f"Document ID: {d['id']}\nTitle: {d['title']}\nSource: {d['metadata']['source']}\nDate: {d['metadata']['date']}\nContent: {d['text']}" for d in docs]
    )

    if not docs:
        docs_text = "(No retrieved documents)"

    prompt = f"{system_instructions}\n\nRetrieved documents:\n{docs_text}\n\nUser question: {question}\n\nAnswer:" 
    return prompt


def run_query(question: str, version: str, tracer=None) -> Dict[str, str]:
    """Run a single query: retrieve docs, call Gemini, and return response.

    tracer: optional LangChainTracer instance (passed to LLM as a callback) to create traces.
    """
    # Retrieve
    docs = retrieve_documents(version, question)

    prompt = build_prompt(question, docs)

    # --- LLM call (Gemini) ---
    if ChatGoogleGenerativeAI is None:
        raise RuntimeError(
            "Required packages not installed. Install requirements.txt and try again."
        )

    # Instantiate Gemini LLM. We pass the tracer via callbacks if available so LangSmith
    # gets the events. The exact argument names may vary with package versions.
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key or gemini_api_key == "your_gemini_api_key_here":
        raise RuntimeError("Please set GEMINI_API_KEY in the .env file before running.")

    # Create tracer if not provided
    callbacks = [tracer] if tracer is not None else None

    # NOTE: The class and parameter names for the langchain-google-genai wrapper can
    # differ between releases. This code uses a plausible constructor: GoogleGemini(...)
    # which accepts `model` or `model_name` and `api_key`, and `callbacks`.
    # Instantiate the chat model. The ChatGoogleGenerativeAI class accepts `model` and `api_key`.
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=gemini_api_key)
    except TypeError:
        # fallback parameter name
        llm = ChatGoogleGenerativeAI(model_name="gemini-2.0-flash", api_key=gemini_api_key)

    # Invoke the chat model with a single human message containing the prompt.
    try:
        # ChatGoogleGenerativeAI.invoke expects a sequence of messages; using a human-only message here.
        res = llm.invoke([("human", prompt)])
        # res is an AIMessage; extract textual content. It may be a string or a list of content blocks.
        if hasattr(res, "content"):
            if isinstance(res.content, str):
                answer = res.content
            elif isinstance(res.content, list):
                # Try to extract 'text' fields or join string parts
                parts = []
                for item in res.content:
                    if isinstance(item, dict) and "text" in item:
                        parts.append(item["text"])
                    elif isinstance(item, str):
                        parts.append(item)
                answer = "\n".join(parts).strip()
            else:
                answer = str(res.content)
        else:
            answer = str(res)
    except Exception as e:
        raise RuntimeError(f"LLM call failed: {e}")

    # Build a simple trace payload to print and (optionally) log via tracer.
    trace = {
        "question": question,
        "version": version,
        "retrieved_documents": docs,
        "prompt": prompt,
        "answer": answer,
    }

    return trace


def main():
    load_dotenv()

    # Create a LangSmith tracer that will send traces to the LangSmith project.
    # This uses the LangChain Core tracer (LangChainTracer) which sends data to
    # LangSmith via the langsmith client. It requires LANGSMITH_API_KEY and will
    # associate runs with the provided project name.
    tracer = None
    if LangChainTracer is not None:
        project = os.environ.get("LANGSMITH_PROJECT", "Zen_Project")
        tracer = LangChainTracer(project_name=project)

    test_questions = [
        "What is the yield strength of Fe 550D 16mm bars?",
        "What's the current price of TMT 12mm per MT?",
        "How long does delivery to Ranchi take?",
    ]

    # Run both versions
    for version in ("buggy", "fixed"):
        print(f"\n--- Running version: {version} ---")
        for q in test_questions:
            print(f"\nQuestion: {q}")
            try:
                trace = run_query(q, version, tracer=tracer)
                # Print concise response and cite retrieved docs
                print("Answer:\n", trace["answer"].strip())

                # Also dump the trace payload to a local file for inspection
                outdir = "langsmith_traces"
                os.makedirs(outdir, exist_ok=True)
                fname = os.path.join(outdir, f"trace_{version}_{abs(hash(q)) % (10**8)}.json")
                with open(fname, "w", encoding="utf-8") as f:
                    json.dump(trace, f, indent=2, ensure_ascii=False)
                print(f"Trace saved to: {fname}")
            except Exception as e:
                print(f"Error running query: {e}")


if __name__ == "__main__":
    main()

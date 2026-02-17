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
        # Test case 1: Yield strength of Fe 550D 16mm
        {
            "id": "fe550d_16mm_spec_current",
            "title": "Fe 550D 16mm specifications",
            "text": (
                "Yield Strength: 565 N/mm² (per IS 1786:2008)."
            ),
            "metadata": {"source": "spec_sheet_2024_current.pdf", "date": "2024-11-01"},
        },
        # Test case 2: Current price of TMT 12mm
        {
            "id": "tmt_12mm_price_current",
            "title": "TMT 12mm pricing",
            "text": "Price: ₹52,500 per MT.",
            "metadata": {"source": "pricing_november_2024.pdf", "date": "2024-11-15"},
        },
        # Test case 3: Delivery time to Ranchi
        {
            "id": "delivery_ranchi_current",
            "title": "Delivery times and logistics",
            "text": "Delivery time to Ranchi: 5-7 business days for orders up to 200 MT. Express delivery available for 3-4 days at additional cost.",
            "metadata": {"source": "logistics_guide_2024.pdf", "date": "2024-11-01"},
        },
        # Test case 4: Product availability (Fe 500D 25mm)
        {
            "id": "product_availability_current",
            "title": "Product availability and inventory",
            "text": "Currently stocked sizes: Fe 550D in 8mm, 10mm, 12mm, 16mm, 20mm. Fe 500D available in 12mm, 16mm, 20mm. For special sizes like 25mm, please consult our inventory team.",
            "metadata": {"source": "inventory_list_2024.pdf", "date": "2024-11-15"},
        },
        # Test case 5: Difference between Fe 500 and Fe 550D
        {
            "id": "fe500_vs_fe550d_current",
            "title": "Fe 500 vs Fe 550D comparison",
            "text": "Fe 550D has higher yield strength (565 N/mm² vs 500 N/mm²), better ductility (minimum elongation 14.5% vs 12%), and enhanced weldability, making it suitable for seismic zones as per IS 13920. Fe 500 is standard grade for general construction. Fe 550D has approximately 8-10% price premium over Fe 500.",
            "metadata": {"source": "product_comparison_2024.pdf", "date": "2024-11-01"},
        },
        # Test case 6: Tensile strength of Fe 550D 16mm
        {
            "id": "fe550d_tensile_current",
            "title": "Fe 550D tensile strength specifications",
            "text": "Minimum tensile strength: 585 N/mm² as per IS 1786:2008. Tensile to yield ratio: minimum 1.08.",
            "metadata": {"source": "spec_sheet_2024_current.pdf", "date": "2024-11-01"},
        },
        # Test case 7: Price for TMT 16mm
        {
            "id": "tmt_16mm_price_current",
            "title": "TMT 16mm pricing",
            "text": "Price: ₹53,200 per MT (as of November 2024).",
            "metadata": {"source": "pricing_november_2024.pdf", "date": "2024-11-15"},
        },
        # Test case 8: Delivery cost to Ranchi
        {
            "id": "delivery_cost_ranchi_current",
            "title": "Delivery costs by location",
            "text": "Delivery cost to Ranchi: ₹2,500 per MT. Delivery cost to Jamshedpur: ₹1,800 per MT. Delivery cost to Dhanbad: ₹2,200 per MT.",
            "metadata": {"source": "logistics_pricing_2024.pdf", "date": "2024-11-01"},
        },
        # Test case 9: Chemical composition of TMT bars
        {
            "id": "tmt_chemical_composition_current",
            "title": "TMT bar chemical composition",
            "text": "TMT bars chemical composition as per IS 1786:2008: Carbon (C): maximum 0.25%, Manganese (Mn): present for strength, Sulfur (S): maximum 0.055%, Phosphorus (P): maximum 0.055%. Actual composition varies by grade and manufacturer specifications.",
            "metadata": {"source": "technical_specs_2024.pdf", "date": "2024-11-01"},
        },
        # Test case 10: Engineering guidance for Fe 550D in high-rise buildings
        {
            "id": "engineering_guidance_current",
            "title": "Engineering guidelines for structural applications",
            "text": "Fe 550D is suitable for high-stress applications including high-rise buildings, bridges, and seismic-resistant structures. For specific structural engineering questions regarding foundation design, load calculations, and building codes compliance, consultation with our technical team and a licensed structural engineer is required. We provide material certifications and test reports for all structural applications.",
            "metadata": {"source": "engineering_guidelines_2024.pdf", "date": "2024-11-01"},
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
        {
            "id": "delivery_ranchi_old",
            "title": "Old delivery times",
            "text": "Delivery time to Ranchi: 7-10 business days.",
            "metadata": {"source": "logistics_guide_2023.pdf", "date": "2023-06-01"},
        },
        {
            "id": "tmt_16mm_price_old",
            "title": "TMT 16mm old pricing",
            "text": "Price: ₹49,000 per MT.",
            "metadata": {"source": "pricing_Q2_2024.pdf", "date": "2024-06-01"},
        },
        {
            "id": "delivery_cost_ranchi_old",
            "title": "Old delivery costs",
            "text": "Delivery cost to Ranchi: ₹3,000 per MT.",
            "metadata": {"source": "logistics_pricing_2023.pdf", "date": "2023-06-01"},
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

    # Improved keyword-based retrieval for all test cases
    q = query.lower()
    retrieved: List[Dict] = []
    
    # Test cases 1, 6: Yield/tensile strength of Fe 550D
    if any(k in q for k in ["yield", "tensile", "strength", "fe 550d", "fe550d"]):
        for d in docs:
            if any(x in d["id"] for x in ["spec", "tensile", "fe550d"]):
                retrieved.append(d)
    
    # Test cases 2, 7: TMT pricing (12mm or 16mm)
    if any(k in q for k in ["price", "cost", "tmt", "per mt"]) and "delivery" not in q:
        for d in docs:
            if "price" in d["id"] and "tmt" in d["id"]:
                # Match specific size if mentioned
                if "12mm" in q and "12mm" in d["id"]:
                    retrieved.append(d)
                elif "16mm" in q and "16mm" in d["id"]:
                    retrieved.append(d)
                elif "12mm" not in q and "16mm" not in q:
                    # If no size specified, return all pricing docs
                    retrieved.append(d)
    
    # Test case 3: Delivery time
    if any(k in q for k in ["delivery time", "how long", "delivery", "take"]) and "cost" not in q:
        for d in docs:
            if "delivery" in d["id"] and "ranchi" in d["id"] and "cost" not in d["id"]:
                retrieved.append(d)
    
    # Test case 4: Product availability
    if any(k in q for k in ["offer", "available", "availability", "stock", "fe 500d", "25mm"]):
        for d in docs:
            if "availability" in d["id"] or "inventory" in d["id"]:
                retrieved.append(d)
    
    # Test case 5: Fe 500 vs Fe 550D comparison
    if any(k in q for k in ["difference", "compare", "vs", "fe 500", "fe500"]):
        for d in docs:
            if "fe500" in d["id"] or "comparison" in d["id"]:
                retrieved.append(d)
    
    # Test case 8: Delivery cost
    if any(k in q for k in ["delivery cost", "delivery charge"]) or ("cost" in q and "ranchi" in q):
        for d in docs:
            if "cost" in d["id"] and "delivery" in d["id"]:
                retrieved.append(d)
    
    # Test case 9: Chemical composition
    if any(k in q for k in ["chemical", "composition", "carbon", "sulfur", "phosphorus", "manganese"]):
        for d in docs:
            if "chemical" in d["id"] or "composition" in d["id"]:
                retrieved.append(d)
    
    # Test case 10: Engineering guidance
    if any(k in q for k in ["building", "foundation", "structural", "engineer", "story", "high-rise"]):
        for d in docs:
            if "engineering" in d["id"] or "guidance" in d["id"] or "structural" in d["id"]:
                retrieved.append(d)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_retrieved = []
    for d in retrieved:
        if d["id"] not in seen:
            seen.add(d["id"])
            unique_retrieved.append(d)
    
    return unique_retrieved


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
    gemini_api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not gemini_api_key or gemini_api_key == "your_gemini_api_key_here":
        raise RuntimeError("Please set GEMINI_API_KEY in the .env file before running.")

    # Create tracer if not provided
    callbacks = [tracer] if tracer is not None else None

    # NOTE: The class and parameter names for the langchain-google-genai wrapper can
    # differ between releases. This code uses a plausible constructor: GoogleGemini(...)
    # which accepts `model` or `model_name` and `api_key`, and `callbacks`.
    # Instantiate the chat model. The ChatGoogleGenerativeAI class accepts `model` and `api_key`.
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=gemini_api_key)
    except TypeError:
        # fallback parameter name
        llm = ChatGoogleGenerativeAI(model_name="gemini-2.5-flash", google_api_key=gemini_api_key)

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

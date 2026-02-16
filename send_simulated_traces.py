import os
import json
from datetime import datetime, timezone
import uuid

from dotenv import load_dotenv

load_dotenv()

from langsmith import Client

# Import helper functions from zenbot
from zenbot import retrieve_documents, build_prompt


def simulate_answer(question: str, docs: list[dict]) -> str:
    if not docs:
        return "I don't have information about delivery times to Ranchi in the retrieved documents."

    # If contains spec
    for d in docs:
        if "spec" in d["id"] or "fe550d" in d["id"]:
            # Expect spec text like 'Yield Strength: 565 N/mm² (per IS 1786:2008).'
            return f"According to {d['metadata']['source']} (date: {d['metadata']['date']}): {d['text']}"

    for d in docs:
        if "price" in d["id"] or "tmt" in d["id"]:
            return f"Price: {d['text']} (source: {d['metadata']['source']}, date: {d['metadata']['date']})"

    return "I don't have the requested information in the retrieved documents."


def create_and_send_runs():
    client = Client(api_key=os.environ.get("LANGSMITH_API_KEY"))
    project = os.environ.get("LANGSMITH_PROJECT", "Zen_Project")

    questions = [
        "What is the yield strength of Fe 550D 16mm bars?",
        "What's the current price of TMT 12mm per MT?",
        "How long does delivery to Ranchi take?",
    ]

    versions = ["buggy", "fixed"]

    outdir = "langsmith_traces"
    os.makedirs(outdir, exist_ok=True)

    created = []

    for version in versions:
        for q in questions:
            docs = retrieve_documents(version, q)
            prompt = build_prompt(q, docs)
            answer = simulate_answer(q, docs)

            run_id = uuid.uuid4()
            now = datetime.now(timezone.utc)

            # Create a run in LangSmith
            try:
                client.create_run(
                    id=str(run_id),
                    project_name=project,
                    name=f"zenbot_{version}",
                    run_type="llm",
                    inputs={
                        "question": q,
                        "retrieved_documents": [{
                            "id": d["id"],
                            "title": d.get("title"),
                            "source": d.get("metadata", {}).get("source"),
                            "date": d.get("metadata", {}).get("date"),
                        } for d in docs],
                        "prompt": prompt,
                    },
                    outputs={"answer": answer},
                    start_time=now,
                    end_time=now,
                )
                created.append(str(run_id))
            except Exception as e:
                print(f"Failed to create run in LangSmith: {e}")

            # Save local JSON trace
            fname = os.path.join(outdir, f"sim_trace_{version}_{abs(hash(q)) % (10**8)}.json")
            with open(fname, "w", encoding="utf-8") as f:
                json.dump({
                    "id": str(run_id),
                    "project": project,
                    "version": version,
                    "question": q,
                    "retrieved_documents": docs,
                    "prompt": prompt,
                    "answer": answer,
                }, f, indent=2, ensure_ascii=False)
            print(f"Saved simulated trace: {fname}")

    print("Created runs:", created)


if __name__ == "__main__":
    create_and_send_runs()

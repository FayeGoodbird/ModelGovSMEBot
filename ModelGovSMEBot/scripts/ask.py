"""Interactive CLI for the Model Governance SME Bot.

Usage:
    python scripts/ask.py
    python scripts/ask.py --jurisdiction UK
    python scripts/ask.py --jurisdiction EU --doc-type regulation
    python scripts/ask.py --provider anthropic --model claude-sonnet-4-5-20250929

Options:
    --jurisdiction   Filter to US | EU | UK | FSB
    --doc-type       Filter by document type (supervisory_guidance, regulation, etc.)
    --provider       LLM provider: openai (default) | anthropic
    --model          Model name (overrides LLM_MODEL env var)
    --top-k          Number of chunks to retrieve (default: 6)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(override=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the Model Governance SME Bot.")
    parser.add_argument("--jurisdiction", help="Filter: US | EU | UK | FSB")
    parser.add_argument("--doc-type", dest="doc_type",
                        help="Filter: supervisory_guidance | regulation | guideline | report | ...")
    parser.add_argument("--provider", default=None, help="LLM provider: openai | anthropic")
    parser.add_argument("--model", default=None, help="Model name within the provider")
    parser.add_argument("--top-k", dest="top_k", type=int, default=6)
    args = parser.parse_args()

    # Allow CLI flags to override env vars
    if args.provider:
        os.environ["LLM_PROVIDER"] = args.provider
    if args.model:
        os.environ["LLM_MODEL"] = args.model

    from services.rag_pipeline import build_rag_chain, VECTOR_STORE_DIR

    if not VECTOR_STORE_DIR.exists():
        sys.exit("ERROR: Vector store not found. Run  python scripts/ingest.py  first.")

    print("Building RAG chain...")
    chain = build_rag_chain(
        jurisdiction=args.jurisdiction,
        doc_type=args.doc_type,
        top_k=args.top_k,
    )

    provider = os.environ.get("LLM_PROVIDER", "openai")
    model = os.environ.get("LLM_MODEL", "gpt-4o" if provider == "openai" else "claude-sonnet-4-5-20250929")
    active_filters = []
    if args.jurisdiction:
        active_filters.append(f"jurisdiction={args.jurisdiction}")
    if args.doc_type:
        active_filters.append(f"doc_type={args.doc_type}")

    print(f"Model: {provider}/{model}")
    if active_filters:
        print(f"Filters: {', '.join(active_filters)}")
    print("Type your question, or 'quit' to exit.\n")

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question or question.lower() in ("quit", "exit", "q"):
            break

        response = chain.invoke(question)

        print(f"\nAnswer:\n{response['answer']}\n")

        print("Sources:")
        seen = set()
        for doc in response.get("context", []):
            m = doc.metadata
            key = (m.get("doc_id"), m.get("page"))
            if key in seen:
                continue
            seen.add(key)
            print(f"  - {m.get('display_name', m.get('source', '?'))} "
                  f"[{m.get('jurisdiction', '?')}] p.{m.get('page', '?')}")
        print()


if __name__ == "__main__":
    main()

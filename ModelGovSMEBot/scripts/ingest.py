"""Ingest all regulatory PDFs into ChromaDB using LangChain.

Usage:
    python scripts/ingest.py [--force-reindex]

Loads each PDF via LangChain's PyMuPDFLoader, enriches every page with
regulatory metadata from the catalog (jurisdiction, doc_type, etc.),
splits with RecursiveCharacterTextSplitter, and upserts into a local
Chroma collection.

--force-reindex  deletes and recreates the collection before indexing.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(override=True)

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from services.regulatory_catalog import REGULATORY_SOURCES

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
COLLECTION_NAME = "regulatory_corpus"

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200


def build_embeddings():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set.")
    model = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
    return OpenAIEmbeddings(model=model, api_key=api_key)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest regulatory PDFs into ChromaDB.")
    parser.add_argument("--force-reindex", action="store_true",
                        help="Drop and recreate the collection before indexing.")
    args = parser.parse_args()

    embeddings = build_embeddings()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    if args.force_reindex and VECTOR_STORE_DIR.exists():
        import shutil
        shutil.rmtree(VECTOR_STORE_DIR)
        print("--force-reindex: cleared existing vector store.")

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(VECTOR_STORE_DIR),
    )

    total_chunks = 0

    for source in REGULATORY_SOURCES:
        pdf_path = RAW_DIR / source.filename
        if not pdf_path.exists():
            print(f"  [SKIP] {source.display_name} — PDF not found at {pdf_path}")
            continue

        print(f"\n  {source.display_name}")
        print(f"    jurisdiction={source.jurisdiction}  doc_type={source.doc_type}")

        loader = PyMuPDFLoader(str(pdf_path))
        pages = loader.load()

        # Enrich every page with catalog metadata
        for doc in pages:
            doc.metadata.update({
                "doc_id": source.doc_id,
                "jurisdiction": source.jurisdiction,
                "doc_type": source.doc_type,
                "display_name": source.display_name,
                "source_filename": source.filename,
            })

        chunks = splitter.split_documents(pages)
        print(f"    {len(pages)} pages -> {len(chunks)} chunks")

        vectorstore.add_documents(chunks)
        print(f"    indexed {len(chunks)} chunks")
        total_chunks += len(chunks)

    print(f"\nDone. Indexed {total_chunks} chunks total.")
    print(f"Vector store: {VECTOR_STORE_DIR}")


if __name__ == "__main__":
    main()

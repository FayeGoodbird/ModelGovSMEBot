# Model Governance SME Bot

A domain-specific RAG chatbot that answers questions on **model risk management and AI governance in banking**, grounded exclusively in official regulatory publications from US, EU, and UK regulators and international standard-setters.

Built with **LangChain** for the RAG layer, supporting pluggable LLM providers (OpenAI, Anthropic, and others) without code changes.

---

## Purpose

Banks operate under increasingly complex and jurisdiction-specific model governance obligations. Practitioners — model developers in the first line of defence (1LoD) or model risk officers in the second line (2LoD) — need fast, reliable access to what specific regulators actually require, without manually searching through dozens of PDFs.

This bot answers questions such as:

- *"What does the PRA require for model validation independence?"*
- *"How does the EU AI Act classify credit scoring models, and what obligations apply?"*
- *"Compare the US SR 11-7 and UK SS1/23 requirements for model documentation."*
- *"As a 2LoD validator, what does the EBA say about machine learning models in IRB?"*

Answers are grounded in retrieved source excerpts with explicit document citations, jurisdiction labels, and page references.

---

## Quick Start

**Prerequisites:** Python 3.11+, an OpenAI API key (always required for embeddings).

```bash
git clone <repo-url>
cd ModelGovSMEBot
pip install -r requirements.txt
```

Create a `.env` file:

```
OPENAI_API_KEY=sk-...
```

Then run the three setup steps once:

```bash
python main.py              # Step 1: download all 13 regulatory PDFs
python scripts/ingest.py    # Step 2: embed and index into ChromaDB
python scripts/ask.py       # Step 3: start asking questions
```

At the `Question:` prompt, type any model governance question and press Enter. Type `quit` to exit.

---

## Regulatory Corpus

13 official publications across 4 jurisdictions, covering both generic model governance and AI-specific model governance:

| Jurisdiction | Generic MRM | AI-specific | Total |
|---|---|---|---|
| United States | 1 | 2 | 3 |
| European Union | 2 | 3 | 5 |
| United Kingdom | 1 | 3 | 4 |
| FSB (international) | — | 1 | 1 |
| **Total** | **4** | **9** | **13** |

Full source list with rationale: [`docs/corpus_sources.md`](docs/corpus_sources.md)

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Layer 1 — Ingestion Pipeline                        │
│  Sync regulatory PDFs from official regulator URLs  │
└──────────────────────┬──────────────────────────────┘
                       │  data/raw/*.pdf
┌──────────────────────▼──────────────────────────────┐
│  Layer 2 — LangChain RAG                            │
│  PyMuPDFLoader -> TextSplitter -> Chroma            │
│  Retriever -> Prompt -> LLM (OpenAI / Anthropic)    │
└──────────────────────┬──────────────────────────────┘
                       │  (Layer 3: not yet started)
┌──────────────────────▼──────────────────────────────┐
│  Layer 3 — FastAPI service + chat UI (TODO)         │
└─────────────────────────────────────────────────────┘
```

### Layer 1 — Ingestion Pipeline

- HTTP sync engine with `If-None-Match` / SHA-256 change detection — only re-downloads changed documents
- 13 sources registered in [`services/regulatory_catalog.py`](services/regulatory_catalog.py), each carrying `jurisdiction` and `doc_type` metadata
- Run `python main.py` for a one-shot sync, or `python periodic_sync.py` for automatic 24-hour refresh

### Layer 2 — LangChain RAG

**Ingest** (`scripts/ingest.py`):
- `PyMuPDFLoader` loads each PDF page-by-page
- Catalog metadata (`jurisdiction`, `doc_type`, `display_name`) is injected into every page's metadata
- `RecursiveCharacterTextSplitter` (1500 chars, 200 overlap) splits into chunks
- Chunks are embedded with OpenAI `text-embedding-3-small` and stored in a local **ChromaDB** collection

**Pipeline** (`services/rag_pipeline.py`):
- Built with **LangChain LCEL** (Expression Language)
- Retriever supports pre-filtering by `jurisdiction` and/or `doc_type` via ChromaDB metadata filters
- LLM is selected at runtime via `LLM_PROVIDER` env var — no code changes needed to switch models
- Returns `{"answer": str, "context": [Document, ...]}` — citations are extracted from document metadata

**Query** (`scripts/ask.py`):
- Interactive CLI with optional jurisdiction/doc_type filters and provider/model flags

---

## Project Structure

```
ModelGovSMEBot/
├── main.py                        # One-shot document sync
├── periodic_sync.py               # Scheduled sync (every 24 h)
├── requirements.txt
├── .env                           # API keys (git-ignored)
│
├── services/
│   ├── regulatory_models.py       # Protocol types for the ingestion layer
│   ├── regulatory_sources.py      # Fetch strategies (DirectHttpSource, etc.)
│   ├── regulatory_catalog.py      # 13-source registry with jurisdiction metadata
│   ├── document_fetcher.py        # HTTP sync engine with change detection
│   └── rag_pipeline.py            # LangChain LCEL RAG chain (configurable LLM)
│
├── scripts/
│   ├── ingest.py                  # Load PDFs -> split -> embed -> store in ChromaDB
│   └── ask.py                     # Interactive CLI to query the bot
│
├── data/
│   ├── raw/                       # Downloaded PDFs (git-ignored)
│   └── vector_store/              # ChromaDB files (git-ignored)
│
└── docs/
    └── corpus_sources.md          # Source reference with rationale
```

---

## Setup

**Prerequisites:** Python 3.11+

```bash
git clone <repo-url>
cd ModelGovSMEBot
pip install -r requirements.txt
```

Create a `.env` file in the project root. `OPENAI_API_KEY` is **always required** — it is used for embeddings even when the LLM is Anthropic:

```
# Always required (embeddings use OpenAI regardless of LLM provider)
OPENAI_API_KEY=sk-...

# Optional: override the default LLM model
LLM_MODEL=gpt-4o

# Optional: switch to Anthropic as the LLM
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-sonnet-4-6

# Optional: override the embedding model
EMBEDDING_MODEL=text-embedding-3-small
```

---

## Usage

### Step 1 — Download the corpus

```bash
python main.py
```

Downloads all 13 regulatory PDFs into `data/raw/`. Safe to re-run — only changed documents are re-downloaded.

### Step 2 — Index into ChromaDB

```bash
python scripts/ingest.py
```

Loads, splits, and embeds every PDF into `data/vector_store/`. Re-run after adding new documents.

To rebuild the index from scratch (e.g. after changing chunk settings):

```bash
python scripts/ingest.py --force-reindex
```

### Step 3 — Ask questions

```bash
# Default: OpenAI gpt-4o, all jurisdictions
python scripts/ask.py

# Filter to UK sources only
python scripts/ask.py --jurisdiction UK

# Filter to EU regulations only
python scripts/ask.py --jurisdiction EU --doc-type regulation

# Switch to Anthropic on the fly (overrides .env)
python scripts/ask.py --provider anthropic --model claude-sonnet-4-6

# Retrieve more source chunks per answer
python scripts/ask.py --top-k 10
```

Valid `--jurisdiction` values: `US` | `EU` | `UK` | `FSB`  
Valid `--doc-type` values: `supervisory_guidance` | `regulation` | `guideline` | `technical_standard` | `discussion_paper` | `framework` | `report`

Each answer is followed by a deduplicated list of cited sources with page numbers.

### Programmatic use

```python
from dotenv import load_dotenv
load_dotenv(override=True)

from services.rag_pipeline import build_rag_chain

chain = build_rag_chain(jurisdiction="UK")
result = chain.invoke("What does PRA SS1/23 say about model validation?")

print(result["answer"])
for doc in result["context"]:
    print(doc.metadata["display_name"], doc.metadata["jurisdiction"], "p.", doc.metadata["page"])
```

---

## Switching LLM providers

No code changes required — set env vars and re-run. Embeddings always use OpenAI regardless of the LLM provider.

| Provider | Required env vars |
|---|---|
| OpenAI (default) | `OPENAI_API_KEY`; optionally `LLM_MODEL=gpt-4o` |
| Anthropic | `LLM_PROVIDER=anthropic`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`; optionally `LLM_MODEL=claude-sonnet-4-6` |

---

## Roadmap

- [x] Layer 1 — Ingestion pipeline
- [x] Layer 2 — LangChain RAG layer
- [ ] Layer 3 — FastAPI service + chat UI

---

## Tech stack

| Component | Technology |
|---|---|
| HTTP sync | `httpx` with ETag / SHA-256 change detection |
| PDF loading | LangChain `PyMuPDFLoader` |
| Text splitting | LangChain `RecursiveCharacterTextSplitter` |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector store | ChromaDB (local persistent) |
| RAG chain | LangChain LCEL |
| LLM | OpenAI / Anthropic (configurable via env var) |
| Scheduling | APScheduler |

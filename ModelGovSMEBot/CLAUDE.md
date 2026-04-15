# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Instructions for Claude

At the end of any session where you modify code, architecture, or the corpus, update this CLAUDE.md to reflect the current state of the project, also update the README.md accordingly.

## Project purpose

**Model Governance SME Bot** — a domain-specific RAG chatbot that answers questions on model risk management and AI governance in banking, grounded exclusively in official regulatory publications from US, EU, UK, and FSB. Target users are practitioners in 1LoD (model developers/owners) and 2LoD (model risk officers/validators).

---

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# --- Layer 1: Document sync ---

# One-shot sync: fetch all regulatory documents into data/raw/
python main.py

# Continuous sync: runs immediately then every 24 hours (APScheduler, blocking)
python periodic_sync.py

# --- Layer 2: RAG pipeline ---

# Ingest PDFs into ChromaDB (run after main.py, or after adding new documents)
python scripts/ingest.py

# Re-index from scratch (drop and recreate the collection)
python scripts/ingest.py --force-reindex

# Interactive CLI to query the bot
python scripts/ask.py

# Filter to UK sources only
python scripts/ask.py --jurisdiction UK

# Filter to EU regulations only
python scripts/ask.py --jurisdiction EU --doc-type regulation

# Use Anthropic instead of OpenAI at runtime (no code changes needed)
python scripts/ask.py --provider anthropic --model claude-sonnet-4-6
```

No test suite or linter is configured yet.

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

---

## Layer 1 — Document sync engine

### Data flow

```
REGULATORY_SOURCES (services/regulatory_catalog.py)
    ↓  tuple[RegulatoryDocumentSource, ...]
DocumentFetcher.sync_all()  (services/document_fetcher.py)
    ↓  HTTP GET with conditional headers (ETag / Last-Modified)
data/raw/<filename>.pdf            — downloaded document bytes
data/.sync_state/<doc_id>.json     — per-document HTTP cache state
```

### Key design points

- **`RegulatoryDocumentSource` is a Protocol** (`services/regulatory_models.py`). Any frozen dataclass that exposes `doc_id`, `filename`, `display_name`, `jurisdiction`, `doc_type`, and `build_fetch_request() → FetchRequest` satisfies it — no inheritance needed.

- **Two concrete source strategies** in `services/regulatory_sources.py`:
  - `DirectHttpSource` — static URL with optional extra headers (used for Fed, EBA, ECB, PRA, BoE, FSB docs).
  - `OpEuropaPublicationPdfSource` — builds an OP Europa download-handler URL from a `publication_identifier`. Use this (not `EurLexPdfSource`) when the EUR-Lex endpoint returns a WAF challenge or async response. Currently used for the EU AI Act.
  - `EurLexPdfSource` is defined but unused; kept as a reference for direct CELEX-based fetching.

- **Change detection is two-tier**: prefer server-side 304 via `If-None-Match`/`If-Modified-Since`; fall back to SHA-256 comparison when the server doesn't send conditional headers.

- **`DocumentFetcher` is a context manager** and owns its `httpx.Client` lifecycle unless one is injected (useful for tests).

### Adding a new regulatory document

1. Add the URL or publication id as a module-level constant in `services/regulatory_catalog.py`.
2. Instantiate the appropriate source type (`DirectHttpSource` or `OpEuropaPublicationPdfSource`) with a `jurisdiction` and `doc_type` and append it to `REGULATORY_SOURCES`.
3. To support a new publisher pattern, add a new frozen dataclass in `services/regulatory_sources.py` that implements `build_fetch_request()`.
4. Run `python main.py` to download the new PDF, then `python scripts/ingest.py` to index it.

Valid `jurisdiction` values: `"US"` | `"EU"` | `"UK"` | `"FSB"`  
Valid `doc_type` values: `"supervisory_guidance"` | `"regulation"` | `"guideline"` | `"technical_standard"` | `"discussion_paper"` | `"framework"` | `"report"`

---

## Layer 2 — LangChain RAG

### Ingest (`scripts/ingest.py`)

- Reads `REGULATORY_SOURCES` from the catalog to know which PDFs to load.
- `PyMuPDFLoader` loads each PDF page-by-page via LangChain.
- Catalog metadata (`doc_id`, `jurisdiction`, `doc_type`, `display_name`, `source_filename`) is injected into every page's metadata — this is what enables per-jurisdiction filtering at retrieval time.
- `RecursiveCharacterTextSplitter` splits into chunks (1500 chars, 200 overlap).
- Chunks are embedded with OpenAI `text-embedding-3-small` and stored in a local **ChromaDB** collection (`regulatory_corpus`) at `data/vector_store/`.

### RAG pipeline (`services/rag_pipeline.py`)

- Built with **LangChain LCEL** (Expression Language).
- Entry point: `build_rag_chain(jurisdiction=None, doc_type=None, top_k=6)` — returns an LCEL chain that accepts `{"input": question}` and returns `{"answer": str, "context": list[Document], "input": str}`.
- Retriever supports pre-filtering by `jurisdiction` and/or `doc_type` via ChromaDB metadata filters (`$and` when both are set).
- LLM is selected at runtime by `LLM_PROVIDER` env var — no code changes needed.
- `format_docs()` inside the chain prepends `[SOURCE N] display_name | jurisdiction | doc_type | p.X` headers to each retrieved chunk — these are referenced by the system prompt so the LLM can cite sources.
- Embeddings always use OpenAI (hardcoded in both `ingest.py` and `rag_pipeline.py`).

### Query CLI (`scripts/ask.py`)

- Interactive REPL: reads questions from stdin, prints answer + deduplicated source list.
- `--provider` and `--model` flags override `LLM_PROVIDER` / `LLM_MODEL` env vars at runtime.

---

## Regulatory corpus (13 documents, as of April 2026)

| doc_id | Display name | Jurisdiction | doc_type |
|---|---|---|---|
| `fed_sr_11_7_guidance` | Federal Reserve / OCC — SR 11-7 | US | supervisory_guidance |
| `nist_ai_100_1_ai_rmf` | NIST AI RMF 1.0 (NIST AI 100-1) | US | framework |
| `us_treasury_ai_financial_services` | US Treasury — AI in Financial Services (2024) | US | report |
| `eu_reg_2024_1689_ai_act` | Regulation (EU) 2024/1689 — AI Act | EU | regulation |
| `eba_gl_2017_11_internal_governance` | EBA — Guidelines on Internal Governance (EBA/GL/2017/11) | EU | guideline |
| `ecb_ssm_guide_internal_models` | ECB — Guide to Internal Models (SSM, 2025) | EU | supervisory_guidance |
| `eba_ml_irb_follow_up_2023` | EBA — ML for IRB Models Follow-up Report (2023) | EU | report |
| `eba_ai_act_implications_2025` | EBA — AI Act Implications for EU Banking (2025) | EU | report |
| `pra_ss1_23_model_risk_management` | PRA — SS1/23 Model Risk Management | UK | supervisory_guidance |
| `boe_fca_dp5_22_ai_ml` | BoE / FCA — DP5/22 AI and Machine Learning | UK | discussion_paper |
| `boe_ai_public_private_forum` | BoE / FCA — AI Public-Private Forum Final Report (2022) | UK | report |
| `boe_fsif_ai_2025` | BoE — Financial Stability in Focus: AI (April 2025) | UK | report |
| `fsb_ai_ml_financial_services_2017` | FSB — AI and ML in Financial Services (2017) | FSB | discussion_paper |

Full rationale for each source: [`docs/corpus_sources.md`](docs/corpus_sources.md)

---

## Environment variables (`.env`)

```
# Always required (embeddings + default LLM)
OPENAI_API_KEY=...

# Switch to Anthropic LLM (embeddings still use OpenAI)
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=...
LLM_MODEL=claude-sonnet-4-6        # any valid model for the chosen provider

# Optional overrides
EMBEDDING_MODEL=text-embedding-3-small   # default
```

`.env` is git-ignored and already populated with keys.

---

## Project structure

```
ModelGovSMEBot/
├── main.py                        # One-shot document sync (Layer 1)
├── periodic_sync.py               # Scheduled 24h sync (APScheduler)
├── requirements.txt
├── .env                           # API keys (git-ignored)
│
├── services/
│   ├── regulatory_models.py       # Protocol + FetchRequest / SyncResult dataclasses
│   ├── regulatory_sources.py      # DirectHttpSource, OpEuropaPublicationPdfSource, EurLexPdfSource
│   ├── regulatory_catalog.py      # 13-source REGULATORY_SOURCES tuple with metadata
│   ├── document_fetcher.py        # HTTP sync engine with ETag / SHA-256 change detection
│   └── rag_pipeline.py            # LangChain LCEL RAG chain (build_rag_chain)
│
├── scripts/
│   ├── ingest.py                  # Load PDFs → split → embed → store in ChromaDB
│   └── ask.py                     # Interactive CLI to query the bot
│
├── data/
│   ├── raw/                       # Downloaded PDFs (git-ignored)
│   ├── .sync_state/               # Per-doc ETag / SHA cache (git-ignored)
│   └── vector_store/              # ChromaDB files (git-ignored)
│
└── docs/
    └── corpus_sources.md          # Source reference with rationale
```

---

## Roadmap

- [x] Layer 1 — Ingestion pipeline
- [x] Layer 2 — LangChain RAG layer (LCEL, ChromaDB, multi-provider LLM)
- [ ] Layer 3 — FastAPI service + chat UI

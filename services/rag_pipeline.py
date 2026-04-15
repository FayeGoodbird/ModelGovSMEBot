"""LangChain RAG pipeline (LCEL) with configurable LLM and embedding providers.

Provider selection is driven entirely by environment variables:

    LLM_PROVIDER=openai          # "openai" (default) | "anthropic"
    LLM_MODEL=gpt-4o             # any model name valid for the chosen provider
    EMBEDDING_MODEL=text-embedding-3-small  # OpenAI embedding model
    OPENAI_API_KEY=...
    ANTHROPIC_API_KEY=...        # required only when LLM_PROVIDER=anthropic

Usage::

    from services.rag_pipeline import build_rag_chain

    chain = build_rag_chain()                           # unfiltered
    chain = build_rag_chain(jurisdiction="UK")          # UK sources only
    chain = build_rag_chain(doc_type="supervisory_guidance")

    result = chain.invoke("What does SR 11-7 say about model validation?")
    print(result["answer"])
    for doc in result["context"]:
        print(doc.metadata["display_name"], doc.metadata["jurisdiction"])
"""

from __future__ import annotations

import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import OpenAIEmbeddings

VECTOR_STORE_DIR = Path("data/vector_store")
COLLECTION_NAME = "regulatory_corpus"

SYSTEM_PROMPT = """\
You are an expert adviser in model risk management and AI governance regulation \
for the financial services industry. Your knowledge covers official publications \
from US regulators (Federal Reserve / OCC, NIST, US Treasury), EU regulators \
(EBA, ECB, EU AI Act), UK regulators (PRA, BoE, FCA), and the FSB.

Answer the user's question using ONLY the source excerpts provided below. \
For every claim, cite the source by its [SOURCE] label. \
If the sources do not contain enough information to answer, say so explicitly.

When the question spans multiple jurisdictions, structure your answer by jurisdiction. \
Always note whether guidance applies to all model types or specifically to AI/ML models.

{context}"""


def build_rag_chain(
    jurisdiction: str | None = None,
    doc_type: str | None = None,
    top_k: int = 6,
):
    """Return an LCEL chain that accepts a question string and returns
    ``{"answer": str, "context": list[Document], "input": str}``.
    """
    embeddings = _build_embeddings()
    llm = _build_llm()

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(VECTOR_STORE_DIR),
    )

    search_filter = _build_filter(jurisdiction, doc_type)
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": top_k,
            **({"filter": search_filter} if search_filter else {}),
        },
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
    ])

    # LCEL chain: retrieve docs, format them into context, pass to LLM
    def format_docs(docs: list) -> str:
        parts = []
        for i, doc in enumerate(docs, start=1):
            m = doc.metadata
            header = (
                f"[SOURCE {i}] {m.get('display_name', '?')} "
                f"| {m.get('jurisdiction', '?')} "
                f"| {m.get('doc_type', '?')} "
                f"| p.{m.get('page', '?')}"
            )
            parts.append(f"{header}\n\n{doc.page_content}")
        return "\n\n---\n\n".join(parts)

    answer_chain = (
        RunnablePassthrough.assign(context=lambda x: format_docs(x["context"]))
        | prompt
        | llm
        | StrOutputParser()
    )

    # Return answer + raw context docs so callers can show citations
    return (
        RunnableParallel({"context": retriever, "input": RunnablePassthrough()})
        .assign(answer=answer_chain)
    )


# ---------------------------------------------------------------------------
# Provider factories
# ---------------------------------------------------------------------------

def _build_llm():
    provider = os.environ.get("LLM_PROVIDER", "openai").lower()

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set.")
        model = os.environ.get("LLM_MODEL", "claude-sonnet-4-5-20250929")
        return ChatAnthropic(model=model, api_key=api_key, max_tokens=1024)

    # Default: OpenAI
    from langchain_openai import ChatOpenAI
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set.")
    model = os.environ.get("LLM_MODEL", "gpt-4o")
    return ChatOpenAI(model=model, api_key=api_key)


def _build_embeddings():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set.")
    model = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
    return OpenAIEmbeddings(model=model, api_key=api_key)


def _build_filter(jurisdiction: str | None, doc_type: str | None) -> dict | None:
    conditions: list[dict] = []
    if jurisdiction:
        conditions.append({"jurisdiction": jurisdiction})
    if doc_type:
        conditions.append({"doc_type": doc_type})
    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}

# Regulatory Corpus — Source Reference

Documents ingested by the sync engine, grouped by jurisdiction and annotated
with their relevance to **generic model governance** and **AI model governance**
in Banking.  Both dimensions are indexed together so that queries from
1LoD (model developers/owners) and 2LoD (model risk officers/validators)
can be answered regardless of angle.

---

## United States

### Generic model governance

| Source | Why it matters |
|---|---|
| **Federal Reserve / OCC — SR 11-7: Guidance on Model Risk Management** (2011) | The foundational US supervisory standard defining model risk, validation requirements, and governance expectations. Issued jointly by the Fed and OCC; applies to all US bank holding companies and federally regulated institutions. Still the primary reference for US banks and the baseline most global firms align to. |

### AI model governance

| Source | Why it matters |
|---|---|
| **NIST — AI Risk Management Framework 1.0 (NIST AI 100-1)** (2023) | The primary US AI governance framework. Provides voluntary guidance on identifying, assessing, and managing AI risks across the AI lifecycle. Widely cross-referenced by US financial regulators and firms aligning AI model risk programmes to SR 11-7. |
| **US Treasury — Artificial Intelligence in Financial Services: Managing AI-Specific Risks** (2024) | Comprehensive US government assessment of AI model risk, third-party AI exposure, adversarial threats, and governance expectations for US financial institutions. Bridges the policy intent of SR 11-7 to AI-specific risk scenarios. |

---

## European Union

### Generic model governance

| Source | Why it matters |
|---|---|
| **EBA — Guidelines on Internal Governance (EBA/GL/2017/11)** (2017) | EBA's binding guidelines on internal governance for credit institutions. Covers the governance framework for model-related decision-making, the role of management bodies, and internal control functions — the EU complement to SR 11-7 for organisational accountability around models. |
| **ECB — Guide to Internal Models (SSM Supervisory Guide)** (2025 update) | The ECB Banking Supervision guide governing how significant institutions must develop, validate, and maintain internal models (IRBA, IRRBB, market risk, counterparty credit risk). Sets out SSM supervisory expectations in granular technical terms; essential for any EU significant institution. |

### AI model governance

| Source | Why it matters |
|---|---|
| **Regulation (EU) 2024/1689 — Artificial Intelligence Act** (2024) | The EU's binding horizontal AI regulation. Introduces a risk-tier framework and lays down conformity, transparency, and governance obligations for AI systems used in regulated sectors including financial services. Directly relevant to any EU-facing AI model. |
| **EBA — Follow-up Report on Machine Learning for IRB Models** (2023) | EBA's assessment of AI/ML model risk specifically in credit risk (IRB) models. Summarises supervisory expectations for validation, documentation, and governance of ML-based models — the most operationally concrete EU guidance for 1LoD model developers working with AI/ML. |
| **EBA — AI Act: Implications for the EU Banking and Payments Sector** (2025) | Bridges the AI Act obligations to banking practice. The key practical reference for EU banks mapping AI governance requirements under the AI Act; covers classification, conformity assessment, and supervisory coordination between NCA and national AI regulators. |

---

## United Kingdom

### Generic model governance

| Source | Why it matters |
|---|---|
| **PRA — SS1/23: Model Risk Management Principles for Banks** (May 2023) | The UK's primary MRM supervisory statement; the functional equivalent of SR 11-7 for PRA-regulated firms. Sets out seven principles covering model risk culture, identification, governance, validation, and use. Mandatory reference for any UK bank or building society. |

### AI model governance

| Source | Why it matters |
|---|---|
| **BoE / FCA — DP5/22: Artificial Intelligence and Machine Learning** (October 2022) | Joint discussion paper by the Bank of England and FCA. Sets out the UK supervisory perspective on AI/ML model risk, governance expectations, and explainability requirements. Foundational for any UK AI/model governance question; the precursor to future binding UK AI guidance. |
| **BoE / FCA — AI Public-Private Forum Final Report** (February 2022) | Joint BoE/FCA industry forum output on AI adoption, governance, and risk management. Influential practical reference for UK AI model governance best practice; useful 1LoD reference for implementation approaches endorsed by the regulator. |
| **BoE — Financial Stability in Focus: AI in the Financial System** (April 2025) | BoE's latest assessment of AI-related systemic and operational risks in financial services. Key 2LoD reference for understanding the macroprudential and firm-level risk management lens that the BoE expects on AI model use. |

---

## International (FSB)

| Source | Why it matters |
|---|---|
| **FSB — Artificial Intelligence and Machine Learning in Financial Services** (2017) | The foundational cross-jurisdictional paper that placed AI/ML model risk on the global regulatory agenda. Referenced by FSB-member regulators across US, EU, and UK; provides common language and risk taxonomy used in subsequent national guidance. |

---

## Corpus summary

| Jurisdiction | Generic MRM | AI-specific | Total |
|---|---|---|---|
| US | 1 | 2 | 3 |
| EU | 2 | 3 | 5 |
| UK | 1 | 3 | 4 |
| FSB (international) | — | 1 | 1 |
| **Total** | **4** | **9** | **13** |

---

## Coverage notes

- All documents are English-language official publications fetched directly from the
  issuing regulator's or standard-setter's website.
- The EU AI Act is retrieved via the OP Europa download handler rather than EUR-Lex
  directly, to avoid WAF / async-response issues with automated clients.
- `doc_id`, `jurisdiction`, and `doc_type` values for each source are defined in
  [`services/regulatory_catalog.py`](../services/regulatory_catalog.py) and are
  stored as metadata in the ChromaDB vector store, enabling per-jurisdiction and
  per-doc_type filtering at retrieval time.

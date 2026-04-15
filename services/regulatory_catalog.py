"""Curated regulatory documents for model governance RAG.

Sources are grouped by jurisdiction and annotated with:
  - jurisdiction: "US" | "EU" | "UK" | "FSB"
  - doc_type: "supervisory_guidance" | "regulation" | "guideline" |
              "technical_standard" | "discussion_paper" | "framework" | "report"

The distinction between generic model governance and AI-focused sources is
captured in display_name and doc_type; both are indexed together so that
queries from 1LoD/2LoD practitioners can be answered regardless of angle.
"""

from __future__ import annotations

from services.regulatory_models import RegulatoryDocumentSource
from services.regulatory_sources import DirectHttpSource, OpEuropaPublicationPdfSource

# ---------------------------------------------------------------------------
# US — Generic model governance
# ---------------------------------------------------------------------------

# Federal Reserve SR 11-7 attachment (joint Fed/OCC model risk management).
FED_SR_11_7_PDF = (
    "https://www.federalreserve.gov/supervisionreg/srletters/sr1107a1.pdf"
)

# ---------------------------------------------------------------------------
# US — AI model governance
# ---------------------------------------------------------------------------

# NIST AI Risk Management Framework 1.0 (NIST AI 100-1, January 2023).
# The primary US AI governance framework; widely cross-referenced by US
# regulators and firms aligning AI model risk to SR 11-7.
NIST_AI_RMF_PDF = "https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf"

# US Treasury — Managing Artificial Intelligence-Specific Cybersecurity Risks
# in the Financial Sector (2024). Covers AI model risk, third-party AI,
# adversarial attacks, and governance expectations for US financial institutions.
US_TREASURY_AI_PDF = (
    "https://home.treasury.gov/system/files/136/Artificial-Intelligence-in-Financial-Services.pdf"
)

# ---------------------------------------------------------------------------
# EU — Generic model governance
# ---------------------------------------------------------------------------

# EBA Guidelines on internal governance (EBA/GL/2017/11) — English PDF.
EBA_INTERNAL_GOVERNANCE_PDF = (
    "https://www.eba.europa.eu/sites/default/files/documents/10180/2164689/"
    "531e7d72-d8ff-4a24-a69a-c7884fa3e476/"
    "Guidelines%20on%20Internal%20Governance%20(EBA-GL-2017-11)_EN.pdf"
)

# ECB Banking Supervision — Guide to internal models (SSM supervisory guide).
ECB_GUIDE_INTERNAL_MODELS_PDF = (
    "https://www.bankingsupervision.europa.eu/ecb/pub/pdf/"
    "ssm.supervisory_guide202507.en.pdf"
)

# ---------------------------------------------------------------------------
# EU — AI model governance
# ---------------------------------------------------------------------------

# OP Europa publication id for Regulation (EU) 2024/1689 (AI Act) PDF (EN).
# Consolidated legal act CELEX: 32024R1689.
EU_AI_ACT_OP_PUBLICATION_ID = "d79f3e5d-41bc-11f0-b9f2-01aa75ed71a1"

# EBA Follow-up Report on Machine Learning for IRB Models (August 2023).
# Directly addresses AI/ML model risk in credit risk (IRB) models; provides
# EBA's assessment of industry ML practices and supervisory expectations.
EBA_ML_IRB_FOLLOW_UP_PDF = (
    "https://www.eba.europa.eu/sites/default/files/document_library/Publications/"
    "Reports/2023/1061483/Follow-up%20report%20on%20machine%20learning%20for%20IRB%20models.pdf"
)

# EBA — AI Act: Implications for the EU Banking and Payments Sector (2025).
# Bridges the AI Act obligations to banking practice; the key practical
# reference for EU banks mapping AI governance requirements under the AI Act.
EBA_AI_ACT_IMPLICATIONS_PDF = (
    "https://www.eba.europa.eu/sites/default/files/2025-11/"
    "d8b999ce-a1d9-4964-9606-971bbc2aaf89/AI%20Act%20implications%20for%20the%20EU%20banking%20sector.pdf"
)

# ---------------------------------------------------------------------------
# UK — Generic model governance
# ---------------------------------------------------------------------------

# PRA Supervisory Statement SS1/23 — Model Risk Management Principles for Banks
# (May 2023). The UK's primary MRM supervisory statement; functional equivalent
# of SR 11-7 for PRA-regulated firms.
PRA_SS1_23_PDF = (
    "https://www.bankofengland.co.uk/-/media/boe/files/prudential-regulation/"
    "supervisory-statement/2023/ss123.pdf"
)

# ---------------------------------------------------------------------------
# UK — AI model governance
# ---------------------------------------------------------------------------

# Bank of England / FCA Discussion Paper DP5/22 — Artificial Intelligence and
# Machine Learning (October 2022). Joint BoE–FCA paper setting out UK
# supervisory expectations on AI/ML model risk and governance.
BOE_FCA_DP5_22_PDF = (
    "https://www.bankofengland.co.uk/-/media/boe/files/prudential-regulation/"
    "publication/2022/dp5-22--artificial-intelligence-and-machine-learning.pdf"
)

# Bank of England — AI Public-Private Forum Final Report (February 2022).
# Joint BoE/FCA industry forum output on AI adoption, governance, and risk
# management; influential practical reference for UK AI model governance.
BOE_AI_PPF_PDF = (
    "https://www.bankofengland.co.uk/-/media/boe/files/fintech/"
    "ai-public-private-forum-final-report.pdf"
)

# Bank of England — Financial Stability in Focus: Artificial Intelligence in
# the Financial System (April 2025). BoE's latest assessment of AI-related
# systemic and operational risks; key 2LoD / risk management reference.
BOE_FSIF_AI_2025_PDF = (
    "https://www.bankofengland.co.uk/-/media/boe/files/financial-stability-in-focus/"
    "2025/financial-stability-in-focus-artificial-intelligence-in-the-financial-system.pdf"
)

# ---------------------------------------------------------------------------
# International (FSB)
# ---------------------------------------------------------------------------

# Financial Stability Board — Artificial Intelligence and Machine Learning in
# Financial Services (November 2017). The foundational cross-jurisdictional
# paper that placed AI/ML model risk on the global regulatory agenda;
# referenced by FSB-member regulators across US, EU, and UK.
FSB_AI_ML_2017_PDF = "https://www.fsb.org/wp-content/uploads/P011117.pdf"

# ---------------------------------------------------------------------------
# Catalogue
# ---------------------------------------------------------------------------

REGULATORY_SOURCES: tuple[RegulatoryDocumentSource, ...] = (
    # --- US: Generic model governance ---
    DirectHttpSource(
        doc_id="fed_sr_11_7_guidance",
        filename="fed_sr_11_7_model_risk_management.pdf",
        display_name="Federal Reserve / OCC - SR 11-7 Model Risk Management (PDF)",
        url=FED_SR_11_7_PDF,
        jurisdiction="US",
        doc_type="supervisory_guidance",
    ),
    # --- US: AI model governance ---
    DirectHttpSource(
        doc_id="nist_ai_100_1_ai_rmf",
        filename="nist_ai_100_1_ai_risk_management_framework.pdf",
        display_name="NIST - AI Risk Management Framework 1.0 (NIST AI 100-1)",
        url=NIST_AI_RMF_PDF,
        jurisdiction="US",
        doc_type="framework",
    ),
    DirectHttpSource(
        doc_id="us_treasury_ai_financial_services",
        filename="us_treasury_ai_financial_services_2024.pdf",
        display_name="US Treasury - AI in Financial Services: Managing AI-Specific Risks (2024)",
        url=US_TREASURY_AI_PDF,
        jurisdiction="US",
        doc_type="report",
    ),
    # --- EU: Generic model governance ---
    OpEuropaPublicationPdfSource(
        doc_id="eu_reg_2024_1689_ai_act",
        filename="eu_reg_2024_1689_ai_act.pdf",
        display_name="Regulation (EU) 2024/1689 - Artificial Intelligence Act (PDF, OP Europa)",
        publication_identifier=EU_AI_ACT_OP_PUBLICATION_ID,
        jurisdiction="EU",
        doc_type="regulation",
        language="en",
    ),
    DirectHttpSource(
        doc_id="eba_gl_2017_11_internal_governance",
        filename="eba_gl_2017_11_internal_governance_en.pdf",
        display_name="EBA - Guidelines on Internal Governance (EBA/GL/2017/11, EN)",
        url=EBA_INTERNAL_GOVERNANCE_PDF,
        jurisdiction="EU",
        doc_type="guideline",
    ),
    DirectHttpSource(
        doc_id="ecb_ssm_guide_internal_models",
        filename="ecb_ssm_guide_internal_models_en.pdf",
        display_name="ECB - Guide to Internal Models (SSM Supervisory Guide, EN)",
        url=ECB_GUIDE_INTERNAL_MODELS_PDF,
        jurisdiction="EU",
        doc_type="supervisory_guidance",
    ),
    # --- EU: AI model governance ---
    DirectHttpSource(
        doc_id="eba_ml_irb_follow_up_2023",
        filename="eba_ml_irb_follow_up_report_2023.pdf",
        display_name="EBA - Follow-up Report on Machine Learning for IRB Models (2023)",
        url=EBA_ML_IRB_FOLLOW_UP_PDF,
        jurisdiction="EU",
        doc_type="report",
    ),
    DirectHttpSource(
        doc_id="eba_ai_act_implications_2025",
        filename="eba_ai_act_implications_eu_banking_2025.pdf",
        display_name="EBA - AI Act: Implications for the EU Banking and Payments Sector (2025)",
        url=EBA_AI_ACT_IMPLICATIONS_PDF,
        jurisdiction="EU",
        doc_type="report",
    ),
    # --- UK: Generic model governance ---
    DirectHttpSource(
        doc_id="pra_ss1_23_model_risk_management",
        filename="pra_ss1_23_model_risk_management.pdf",
        display_name="PRA - SS1/23 Model Risk Management Principles for Banks (PDF)",
        url=PRA_SS1_23_PDF,
        jurisdiction="UK",
        doc_type="supervisory_guidance",
    ),
    # --- UK: AI model governance ---
    DirectHttpSource(
        doc_id="boe_fca_dp5_22_ai_ml",
        filename="boe_fca_dp5_22_ai_machine_learning.pdf",
        display_name="BoE / FCA - DP5/22 Artificial Intelligence and Machine Learning (PDF)",
        url=BOE_FCA_DP5_22_PDF,
        jurisdiction="UK",
        doc_type="discussion_paper",
    ),
    DirectHttpSource(
        doc_id="boe_ai_public_private_forum",
        filename="boe_ai_public_private_forum_final_report.pdf",
        display_name="BoE / FCA - AI Public-Private Forum Final Report (February 2022)",
        url=BOE_AI_PPF_PDF,
        jurisdiction="UK",
        doc_type="report",
    ),
    DirectHttpSource(
        doc_id="boe_fsif_ai_2025",
        filename="boe_financial_stability_in_focus_ai_2025.pdf",
        display_name="BoE - Financial Stability in Focus: AI in the Financial System (April 2025)",
        url=BOE_FSIF_AI_2025_PDF,
        jurisdiction="UK",
        doc_type="report",
    ),
    # --- International (FSB) ---
    DirectHttpSource(
        doc_id="fsb_ai_ml_financial_services_2017",
        filename="fsb_ai_ml_financial_services_2017.pdf",
        display_name="FSB - Artificial Intelligence and Machine Learning in Financial Services (2017)",
        url=FSB_AI_ML_2017_PDF,
        jurisdiction="FSB",
        doc_type="discussion_paper",
    ),
)

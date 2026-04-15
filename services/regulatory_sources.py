"""Concrete download strategies for different publisher patterns."""

from __future__ import annotations

from dataclasses import dataclass, field

from services.regulatory_models import FetchRequest


@dataclass(frozen=True)
class DirectHttpSource:
    """Static URL (PDF, XML, etc.) with optional extra headers."""

    doc_id: str
    filename: str
    display_name: str
    url: str
    jurisdiction: str
    doc_type: str
    extra_headers: dict[str, str] = field(default_factory=dict)

    def build_fetch_request(self) -> FetchRequest:
        return FetchRequest(url=self.url, headers=dict(self.extra_headers))


@dataclass(frozen=True)
class OpEuropaPublicationPdfSource:
    """
    PDF from the EU Publications Office download-handler.

    Use when EUR-Lex serves async/WAF-wrapped responses for automated clients;
    the publication id is the official OP catalogue entry for the same instrument.
    """

    doc_id: str
    filename: str
    display_name: str
    publication_identifier: str
    jurisdiction: str
    doc_type: str
    language: str = "en"

    def build_fetch_request(self) -> FetchRequest:
        url = (
            "https://op.europa.eu/o/opportal-service/download-handler"
            f"?identifier={self.publication_identifier}&format=PDF&language={self.language}"
        )
        return FetchRequest(url=url)


@dataclass(frozen=True)
class EurLexPdfSource:
    """
    EUR-Lex consolidated act PDF (CELEX id, e.g. 32024R1689).

    May return 202 or WAF challenge HTML for some environments; prefer
    OpEuropaPublicationPdfSource when an OP publication id exists.
    """

    doc_id: str
    filename: str
    display_name: str
    celex: str
    jurisdiction: str
    doc_type: str
    language: str = "EN"

    def build_fetch_request(self) -> FetchRequest:
        url = (
            f"https://eur-lex.europa.eu/legal-content/{self.language}/TXT/PDF/"
            f"?uri=CELEX:{self.celex}"
        )
        return FetchRequest(
            url=url,
            headers={"Accept": "application/pdf,*/*;q=0.8"},
        )

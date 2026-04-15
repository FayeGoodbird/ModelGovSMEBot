"""Shared types for regulatory document sync."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Protocol, runtime_checkable


@dataclass(frozen=True)
class FetchRequest:
    """Resolved HTTP GET the sync engine will perform."""

    url: str
    headers: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SyncResult:
    doc_id: str
    display_name: str
    url: str
    path: Path
    http_status: int
    changed: bool
    bytes_written: int | None
    etag: str | None
    last_modified: str | None
    content_sha256: str | None


@runtime_checkable
class RegulatoryDocumentSource(Protocol):
    """Anything that can describe how to download one corpus file."""

    doc_id: str
    filename: str
    display_name: str
    jurisdiction: str  # ISO-like tag: "US" | "EU" | "UK"
    doc_type: str      # "supervisory_guidance" | "regulation" | "guideline" | "technical_standard" | "discussion_paper"

    def build_fetch_request(self) -> FetchRequest:
        """Return the URL (and optional headers) for this document."""
        ...

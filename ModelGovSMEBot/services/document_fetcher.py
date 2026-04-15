"""Sync engine: HTTP GET with conditional headers, keyed by document id."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import httpx

from services.regulatory_models import FetchRequest, RegulatoryDocumentSource, SyncResult

DEFAULT_TIMEOUT = 120.0
DEFAULT_USER_AGENT = (
    "ModelGovSMEBot/0.1 (regulatory document sync; research / RAG corpus)"
)


class DocumentFetcher:
    """
    Downloads bytes from a :class:`RegulatoryDocumentSource`.

    Uses If-None-Match / If-Modified-Since when the server provides them; otherwise
    relies on content SHA-256 to skip rewriting unchanged files.
    """

    def __init__(
        self,
        data_dir: Path,
        client: httpx.Client | None = None,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        self.data_dir = data_dir
        self.raw_dir = data_dir / "raw"
        self.state_dir = data_dir / ".sync_state"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._own_client = client is None
        self._client = client or httpx.Client(
            timeout=DEFAULT_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": user_agent},
        )

    def close(self) -> None:
        if self._own_client:
            self._client.close()

    def __enter__(self) -> DocumentFetcher:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _state_path(self, doc_id: str) -> Path:
        safe = doc_id.replace("/", "_")
        return self.state_dir / f"{safe}.json"

    def _load_state(self, doc_id: str) -> dict:
        path = self._state_path(doc_id)
        if not path.is_file():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _save_state(self, doc_id: str, state: dict) -> None:
        self._state_path(doc_id).write_text(
            json.dumps(state, indent=2), encoding="utf-8"
        )

    def sync_source(self, source: RegulatoryDocumentSource) -> SyncResult:
        request = source.build_fetch_request()
        return self._sync_request(
            doc_id=source.doc_id,
            display_name=source.display_name,
            filename=source.filename,
            request=request,
        )

    def sync_all(self, sources: tuple[RegulatoryDocumentSource, ...]) -> list[SyncResult]:
        return [self.sync_source(s) for s in sources]

    def _sync_request(
        self,
        doc_id: str,
        display_name: str,
        filename: str,
        request: FetchRequest,
    ) -> SyncResult:
        out_path = self.raw_dir / filename
        state = self._load_state(doc_id)
        url = request.url

        req_headers: dict[str, str] = dict(request.headers)
        if etag := state.get("etag"):
            req_headers.setdefault("If-None-Match", etag)
        if lm := state.get("last_modified"):
            req_headers.setdefault("If-Modified-Since", lm)

        response = self._client.get(url, headers=req_headers)

        if response.status_code == 304:
            return SyncResult(
                doc_id=doc_id,
                display_name=display_name,
                url=url,
                path=out_path,
                http_status=304,
                changed=False,
                bytes_written=None,
                etag=state.get("etag"),
                last_modified=state.get("last_modified"),
                content_sha256=state.get("content_sha256"),
            )

        response.raise_for_status()
        body = response.content
        digest = hashlib.sha256(body).hexdigest()

        if state.get("content_sha256") == digest and out_path.is_file():
            new_state = {
                "url": url,
                "etag": response.headers.get("etag") or state.get("etag"),
                "last_modified": response.headers.get("last-modified")
                or state.get("last_modified"),
                "content_sha256": digest,
            }
            self._save_state(doc_id, new_state)
            return SyncResult(
                doc_id=doc_id,
                display_name=display_name,
                url=url,
                path=out_path,
                http_status=response.status_code,
                changed=False,
                bytes_written=0,
                etag=new_state.get("etag"),
                last_modified=new_state.get("last_modified"),
                content_sha256=digest,
            )

        out_path.write_bytes(body)
        new_state = {
            "url": url,
            "etag": response.headers.get("etag"),
            "last_modified": response.headers.get("last-modified"),
            "content_sha256": digest,
        }
        self._save_state(doc_id, new_state)
        return SyncResult(
            doc_id=doc_id,
            display_name=display_name,
            url=url,
            path=out_path,
            http_status=response.status_code,
            changed=True,
            bytes_written=len(body),
            etag=new_state.get("etag"),
            last_modified=new_state.get("last_modified"),
            content_sha256=digest,
        )

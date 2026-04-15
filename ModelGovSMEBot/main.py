"""Entry point: sync the regulatory document catalog."""

from pathlib import Path

from services.document_fetcher import DocumentFetcher
from services.regulatory_catalog import REGULATORY_SOURCES


def main() -> None:
    project_root = Path(__file__).resolve().parent
    data_dir = project_root / "data"

    with DocumentFetcher(data_dir) as fetcher:
        results = fetcher.sync_all(REGULATORY_SOURCES)

    for result in results:
        extra = ""
        if result.bytes_written is not None and result.bytes_written > 0:
            extra = f" | wrote {result.bytes_written} bytes"
        print(
            f"{result.display_name}\n"
            f"  HTTP {result.http_status} | changed={result.changed} | "
            f"{result.path.name}{extra}"
        )


if __name__ == "__main__":
    main()

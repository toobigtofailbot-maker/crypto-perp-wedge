"""Bounded upstream release and security watch with normalized output only."""

from __future__ import annotations

import json
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import NON_AUTHORITY, EvidenceUnavailableError, RepoIdentity, ResourceDeniedError

Fetcher = Callable[[str], Any]


def _fetch_json(url: str) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "crypto-perp-wedge-project-evidence/1",
        },
        method="GET",
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=10) as response:
        raw = response.read(1_000_001)
    if len(raw) > 1_000_000:
        raise EvidenceUnavailableError("upstream watch response exceeded byte limit")
    return json.loads(raw)


class DependencySecurityWatch:
    """Fetch only repo-pinned URLs and strip all free-form upstream text."""

    def __init__(
        self,
        manifest_path: Path,
        identity: RepoIdentity,
        *,
        fetcher: Fetcher = _fetch_json,
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.manifest_path = manifest_path.resolve()
        self.identity = identity
        self._fetcher = fetcher
        self._now = now

    def _manifest(self) -> dict[str, Any]:
        payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        if payload.get("schema_version") != "hermes_upstream_watch_v1":
            raise EvidenceUnavailableError("upstream watch manifest version is unsupported")
        sources = payload.get("sources")
        if not isinstance(sources, list) or not sources:
            raise EvidenceUnavailableError("upstream watch manifest has no sources")
        for source in sources:
            if set(source) != {"source_id", "kind", "url", "pinned_version"}:
                raise EvidenceUnavailableError("upstream watch source shape is invalid")
            if source["kind"] not in {"github_release", "github_advisories", "pypi"}:
                raise EvidenceUnavailableError("upstream watch source kind is invalid")
            url = source["url"]
            if not isinstance(url, str) or not url.startswith(
                ("https://api.github.com/", "https://pypi.org/pypi/")
            ):
                raise ResourceDeniedError("upstream watch URL is outside the host allowlist")
        return payload

    @staticmethod
    def _normalize(source: dict[str, str], payload: Any) -> dict[str, Any]:
        kind = source["kind"]
        base = {
            "source_id": source["source_id"],
            "kind": kind,
            "source_url": source["url"],
            "pinned_version": source["pinned_version"],
        }
        if kind == "github_release":
            return {
                **base,
                "latest_version": payload.get("tag_name") if isinstance(payload, dict) else None,
                "published_at": payload.get("published_at") if isinstance(payload, dict) else None,
                "release_url": payload.get("html_url") if isinstance(payload, dict) else None,
            }
        if kind == "github_advisories":
            rows = payload if isinstance(payload, list) else []
            return {
                **base,
                "advisories": [
                    {
                        "ghsa_id": row.get("ghsa_id"),
                        "cve_id": row.get("cve_id"),
                        "severity": row.get("severity"),
                        "published_at": row.get("published_at"),
                        "advisory_url": row.get("html_url"),
                    }
                    for row in rows[:100]
                    if isinstance(row, dict)
                ],
            }
        info = payload.get("info", {}) if isinstance(payload, dict) else {}
        vulnerabilities = payload.get("vulnerabilities", []) if isinstance(payload, dict) else []
        return {
            **base,
            "latest_version": info.get("version") if isinstance(info, dict) else None,
            "vulnerabilities": [
                {
                    "id": row.get("id"),
                    "fixed_in": row.get("fixed_in", []),
                    "link": row.get("link"),
                }
                for row in vulnerabilities[:100]
                if isinstance(row, dict)
            ],
        }

    def check(self) -> dict[str, Any]:
        manifest = self._manifest()
        results = []
        for source in manifest["sources"]:
            try:
                payload = self._fetcher(source["url"])
                result = {"status": "available", **self._normalize(source, payload)}
            except (OSError, ValueError) as exc:
                result = {
                    "status": "unknown",
                    "source_id": source["source_id"],
                    "kind": source["kind"],
                    "source_url": source["url"],
                    "pinned_version": source["pinned_version"],
                    "reason": type(exc).__name__,
                }
            results.append(result)
        return {
            "checked_at_utc": self._now()
            .astimezone(UTC)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z"),
            "repo_sha": self.identity.repo_sha,
            "results": results,
            "content_handling": (
                "free-form upstream descriptions are discarded; output cannot grant capabilities"
            ),
            "mutation_policy": "digest/proposal input only; dependency mutation is unavailable",
            "authority": dict(NON_AUTHORITY),
        }

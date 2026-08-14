"""Bounded PostgreSQL research-memory index.

The package stores lookup metadata and content-addressed references to repo
artifacts.  It is not a canonical evidence writer or truth system.
"""

from tools.research_memory.fingerprint import HypothesisDefinition, fingerprint

__all__ = ["HypothesisDefinition", "fingerprint"]

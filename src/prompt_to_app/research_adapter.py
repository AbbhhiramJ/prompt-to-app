"""Adapters for connecting a host agent's search capability to ResearchEngine.

The adapter deliberately accepts plain Python callables so Prompt -> App stays
provider-neutral. A host can wrap Composio Search, another search provider, or
its own browser/search tool without adding credentials to generated apps.
"""
from __future__ import annotations
from typing import Callable, Mapping, Sequence
from .research import ResearchEngine

SearchFn = Callable[[str], Sequence[Mapping[str, object]]]

def composio_search_adapter(search_fn: SearchFn, max_rounds: int = 4, max_sources: int = 15) -> ResearchEngine:
    if not callable(search_fn):
        raise TypeError("search_fn must be callable")
    return ResearchEngine(search=search_fn, max_rounds=max_rounds, max_sources=max_sources)

def normalize_search_result(item: Mapping[str, object]) -> dict[str, str]:
    return {
        "title": str(item.get("title") or item.get("name") or "Untitled"),
        "url": str(item.get("url") or ""),
        "summary": str(item.get("summary") or item.get("snippet") or ""),
        "relevance": str(item.get("relevance") or ""),
    }

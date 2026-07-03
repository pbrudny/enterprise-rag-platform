"""Heuristic prompt-injection detector (PRD sections 6.3.3, 6.4.3).

Deliberately simple pattern matching, not ML-based — the PRD explicitly
allows this as an acceptable ingestion/query-time guardrail, with an
optional LLM-based classifier as a stretch goal (out of scope here, see
enterprise-rag-platform/CLAUDE.md). The same detector instance is used at
both ingestion time (scanning documents before indexing) and query time
(scanning the user's question before retrieval) — one implementation, two
call sites, per the PRD's defense-in-depth layering.
"""

import re
from dataclasses import dataclass

_PATTERNS = [
    r"ignore (all )?(previous|prior|above) instructions",
    r"disregard (all )?(previous|prior|above) instructions",
    r"system prompt",
    r"you are now in (developer|debug) mode",
    r"reveal (your|the) (system prompt|instructions)",
    r"exfiltrate",
    r"act as (if you (are|were)|an?) (unrestricted|jailbroken)",
    r"output (your|the) (system prompt|instructions) verbatim",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _PATTERNS]


@dataclass(frozen=True)
class InjectionScanResult:
    is_suspicious: bool
    matched_patterns: tuple[str, ...]


class PromptInjectionDetector:
    def scan(self, text: str) -> InjectionScanResult:
        matches = tuple(pattern.pattern for pattern in _COMPILED if pattern.search(text))
        return InjectionScanResult(is_suspicious=bool(matches), matched_patterns=matches)

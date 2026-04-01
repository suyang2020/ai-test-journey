from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FileChange:
    """Represents a single changed file from git diff."""

    old_path: str
    new_path: str
    change_type: str
    additions: int
    deletions: int
    patch: str


@dataclass
class DiffSummary:
    """Structured diff data consumed by the analyzer."""

    files: list[FileChange] = field(default_factory=list)
    raw_diff: str = ""


@dataclass
class TestSuggestionReport:
    """Normalized report object for renderer/exporters."""

    summary: str
    risk_level: str
    suggested_tests: list[str]
    edge_cases: list[str]
    automation_priority: list[str]


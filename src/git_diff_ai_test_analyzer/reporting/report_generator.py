from __future__ import annotations

import json

from git_diff_ai_test_analyzer.models.schemas import TestSuggestionReport


class ReportGenerator:
    """Render the analysis result into markdown or JSON."""

    def to_markdown(self, report: TestSuggestionReport) -> str:
        suggested_tests = (
            "\n".join(f"- {item}" for item in report.suggested_tests)
            if report.suggested_tests
            else "- (none)"
        )
        edge_cases = (
            "\n".join(f"- {item}" for item in report.edge_cases)
            if report.edge_cases
            else "- (none)"
        )
        automation_priority = (
            "\n".join(f"- {item}" for item in report.automation_priority)
            if report.automation_priority
            else "- (none)"
        )

        return f"""# AI Testing Suggestion Report

## Summary
{report.summary}

## Risk Level
{report.risk_level}

## Suggested Tests
{suggested_tests}

## Edge Cases
{edge_cases}

## Automation Priority
{automation_priority}
"""

    def to_json(self, report: TestSuggestionReport) -> str:
        return json.dumps(
            {
                "summary": report.summary,
                "risk_level": report.risk_level,
                "suggested_tests": report.suggested_tests,
                "edge_cases": report.edge_cases,
                "automation_priority": report.automation_priority,
            },
            ensure_ascii=False,
            indent=2,
        )


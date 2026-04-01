from __future__ import annotations

import json

from openai import OpenAI

from git_diff_ai_test_analyzer.config import Settings
from git_diff_ai_test_analyzer.models.schemas import DiffSummary, TestSuggestionReport


class AIAnalyzer:
    """Call OpenAI API and convert response into structured report."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key)

    def analyze(self, summary: DiffSummary) -> TestSuggestionReport:
        prompt = self._build_prompt(summary)
        response = self.client.responses.create(
            model=self.settings.openai_model,
            input=prompt,
            temperature=0.2,
        )
        raw_text = response.output_text
        return self._parse_response(raw_text)

    def _build_prompt(self, summary: DiffSummary) -> str:
        file_lines = []
        for file in summary.files:
            file_lines.append(
                f"- {file.new_path} ({file.change_type}, +{file.additions}/-{file.deletions})"
            )
        file_info = "\n".join(file_lines) if file_lines else "- No changed files parsed."

        clipped_diff = summary.raw_diff[: self.settings.max_diff_chars]

        # Ask model for strict JSON for predictable parsing.
        return f"""
You are a senior QA engineer. Analyze this git diff and provide test recommendations.

Changed files:
{file_info}

Diff:
{clipped_diff}

Return JSON only with this schema:
{{
  "summary": "short overall testing summary",
  "risk_level": "low|medium|high",
  "suggested_tests": ["..."],
  "edge_cases": ["..."],
  "automation_priority": ["..."]
}}
""".strip()

    def _parse_response(self, raw_text: str) -> TestSuggestionReport:
        data = json.loads(raw_text)
        return TestSuggestionReport(
            summary=data.get("summary", "No summary"),
            risk_level=data.get("risk_level", "medium"),
            suggested_tests=data.get("suggested_tests", []),
            edge_cases=data.get("edge_cases", []),
            automation_priority=data.get("automation_priority", []),
        )


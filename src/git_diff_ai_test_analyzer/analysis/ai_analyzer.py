from __future__ import annotations

import json

from openai import OpenAI

from git_diff_ai_test_analyzer.config import Settings
from git_diff_ai_test_analyzer.models.schemas import DiffSummary, TestSuggestionReport


class AIAnalyzer:
    """Call an OpenAI-compatible API and convert response into structured report."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,  # None => OpenAI default
        )

    def analyze(self, summary: DiffSummary) -> TestSuggestionReport:
        prompt = self._build_prompt(summary)
        # Use chat.completions for wider OpenAI-compatibility (e.g. Alibaba DashScope).
        response = self.client.chat.completions.create(
            model=self.settings.openai_model,
            messages=[
                {"role": "system", "content": "Return ONLY valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        raw_text = response.choices[0].message.content or ""
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
        cleaned = self._clean_json_text(raw_text)
        data = json.loads(cleaned)
        return TestSuggestionReport(
            summary=data.get("summary", "No summary"),
            risk_level=data.get("risk_level", "medium"),
            suggested_tests=data.get("suggested_tests", []),
            edge_cases=data.get("edge_cases", []),
            automation_priority=data.get("automation_priority", []),
        )

    def _clean_json_text(self, raw_text: str) -> str:
        """Best-effort extraction in case the model wraps JSON in markdown/code fences."""
        text = (raw_text or "").strip()
        if not text:
            return "{}"

        # Remove ```json ... ``` fences
        if text.startswith("```"):
            text = text.strip("`")
            # After stripping, there may still be a leading 'json\n'
            text = text.split("\n", 1)[-1] if "\n" in text else text

        # Extract the first JSON object if extra text exists.
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
        return text


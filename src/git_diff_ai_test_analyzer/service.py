from __future__ import annotations

from git_diff_ai_test_analyzer.analysis.ai_analyzer import AIAnalyzer
from git_diff_ai_test_analyzer.config import Settings
from git_diff_ai_test_analyzer.models.schemas import TestSuggestionReport
from git_diff_ai_test_analyzer.parsing.diff_parser import DiffParser
from git_diff_ai_test_analyzer.reporting.report_generator import ReportGenerator


class AITestAnalysisService:
    """Application service that orchestrates parse -> analyze -> render."""

    def __init__(self, settings: Settings):
        self.diff_parser = DiffParser()
        self.ai_analyzer = AIAnalyzer(settings=settings)
        self.report_generator = ReportGenerator()

    def analyze(self, diff_text: str) -> TestSuggestionReport:
        """Analyze raw diff text and return a structured test suggestion report."""
        diff_summary = self.diff_parser.parse_text(diff_text)
        return self.ai_analyzer.analyze(diff_summary)

    def generate_report(self, diff_file_path: str) -> str:
        """Convenience method (v1 API): parse file, analyze, render markdown."""
        diff_summary = self.diff_parser.parse_file(diff_file_path)
        suggestion_report = self.ai_analyzer.analyze(diff_summary)
        return self.report_generator.to_markdown(suggestion_report)


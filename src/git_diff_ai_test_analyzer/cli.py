from __future__ import annotations

import argparse
from pathlib import Path

from git_diff_ai_test_analyzer.config import load_settings
from git_diff_ai_test_analyzer.service import AITestAnalysisService


def build_arg_parser() -> argparse.ArgumentParser:
    """CLI arguments for analysis execution."""

    parser = argparse.ArgumentParser(
        description="AI test analysis tool based on git diff file."
    )
    parser.add_argument("--diff", required=True, help="Path to git diff file.")
    parser.add_argument(
        "--out",
        default="report/testing_suggestion.md",
        help="Output report path (markdown).",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    settings = load_settings()
    service = AITestAnalysisService(settings=settings)

    report_markdown = service.generate_report(args.diff)
    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report_markdown, encoding="utf-8")

    print(f"Report generated: {out_path}")


if __name__ == "__main__":
    main()


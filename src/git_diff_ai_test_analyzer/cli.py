from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from git_diff_ai_test_analyzer.config import load_settings
from git_diff_ai_test_analyzer.git_ops import (
    GitError,
    git_diff_branches,
    git_diff_range,
)
from git_diff_ai_test_analyzer.models.schemas import TestSuggestionReport
from git_diff_ai_test_analyzer.reporting.report_generator import ReportGenerator
from git_diff_ai_test_analyzer.service import AITestAnalysisService


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AI test analysis tool based on git diff."
    )
    # Diff source (exactly one required, validated post-parse)
    parser.add_argument(
        "--diff",
        default=None,
        help="Path to git diff file.",
    )
    parser.add_argument(
        "--base",
        default=None,
        help="Base branch for comparison (use with --target).",
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Target branch (defaults to HEAD when --base is set).",
    )
    parser.add_argument(
        "--commit-range",
        default=None,
        help="Commit range, e.g. HEAD~3..HEAD",
    )
    # Output
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default=None,
        help="Output format (default: markdown, or json when --ci).",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output file path (default: report/testing_suggestion.md for markdown).",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: JSON to stdout, clean exit codes.",
    )
    return parser


def _validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    """Ensure exactly one diff source is specified."""
    sources = [
        name for name in ("diff", "base", "commit_range")
        if getattr(args, name, None)
    ]
    if len(sources) == 0:
        parser.error(
            "Must specify one diff source: --diff, --base, or --commit-range"
        )
    if len(sources) > 1:
        parser.error(
            f"Only one diff source allowed, got: {', '.join(sources)}"
        )
    if args.target and not args.base:
        parser.error("--target requires --base")


def _get_diff_text(args: argparse.Namespace) -> str:
    if args.diff:
        path = Path(args.diff).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Diff file not found: {path}")
        return path.read_text(encoding="utf-8")
    if args.base:
        target = args.target or "HEAD"
        return git_diff_branches(args.base, target)
    if args.commit_range:
        return git_diff_range(args.commit_range)
    raise AssertionError("No diff source — should have been caught by validation")


def _render(report: TestSuggestionReport, fmt: str) -> str:
    gen = ReportGenerator()
    if fmt == "json":
        return gen.to_json(report)
    return gen.to_markdown(report)


def _empty_report() -> TestSuggestionReport:
    return TestSuggestionReport(
        summary="No changes detected in the diff.",
        risk_level="low",
        suggested_tests=[],
        edge_cases=[],
        automation_priority=[],
    )


def _write_output(output: str, args: argparse.Namespace, fmt: str) -> None:
    if args.ci:
        print(output)
        return

    if args.out:
        out_path = Path(args.out).expanduser().resolve()
    elif fmt == "markdown":
        out_path = Path("report/testing_suggestion.md").resolve()
    else:
        # JSON format, no explicit output file → stdout
        print(output)
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output, encoding="utf-8")
    print(f"Report generated: {out_path}", file=sys.stderr)


def _die(
    msg: str,
    args: argparse.Namespace,
    exit_code: int = 1,
    error_type: str = "Error",
) -> None:
    if args.ci:
        print(json.dumps({"error": msg, "error_type": error_type}))
    else:
        print(f"Error: {msg}", file=sys.stderr)
    sys.exit(exit_code)


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    _validate_args(parser, args)

    ci_mode = args.ci
    fmt = args.format or ("json" if ci_mode else "markdown")

    # Load settings (may fail on missing API key)
    try:
        settings = load_settings()
    except ValueError as e:
        _die(str(e), args, error_type="ConfigError")

    # Get diff text
    try:
        diff_text = _get_diff_text(args)
    except (FileNotFoundError, GitError, OSError) as e:
        _die(str(e), args, error_type=type(e).__name__)

    # Analyze
    try:
        if not diff_text.strip():
            report = _empty_report()
        else:
            service = AITestAnalysisService(settings=settings)
            report = service.analyze(diff_text)
    except Exception as e:
        _die(
            f"Analysis failed: {e}",
            args,
            error_type=type(e).__name__,
        )

    # Render and output
    try:
        output = _render(report, fmt)
        _write_output(output, args, fmt)
    except OSError as e:
        _die(str(e), args, error_type=type(e).__name__)


if __name__ == "__main__":
    main()

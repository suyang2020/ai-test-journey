from __future__ import annotations

from pathlib import Path

from git_diff_ai_test_analyzer.models.schemas import DiffSummary, FileChange


class DiffParser:
    """Parse git diff text into structured file-level changes."""

    def parse_file(self, diff_file_path: str) -> DiffSummary:
        path = Path(diff_file_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Diff file not found: {path}")
        content = path.read_text(encoding="utf-8")
        return self.parse_text(content)

    def parse_text(self, diff_text: str) -> DiffSummary:
        summary = DiffSummary(raw_diff=diff_text)
        chunks = diff_text.split("diff --git ")
        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue
            file_change = self._parse_file_chunk(chunk)
            if file_change:
                summary.files.append(file_change)
        return summary

    def _parse_file_chunk(self, chunk: str) -> FileChange | None:
        lines = chunk.splitlines()
        if not lines:
            return None

        # First line example: a/src/a.py b/src/a.py
        header = lines[0].strip().split()
        if len(header) < 2:
            return None
        old_path = header[0].removeprefix("a/")
        new_path = header[1].removeprefix("b/")

        additions = sum(1 for line in lines if line.startswith("+") and not line.startswith("+++"))
        deletions = sum(1 for line in lines if line.startswith("-") and not line.startswith("---"))
        change_type = "modified"
        if old_path == "/dev/null":
            change_type = "added"
        elif new_path == "/dev/null":
            change_type = "deleted"

        return FileChange(
            old_path=old_path,
            new_path=new_path,
            change_type=change_type,
            additions=additions,
            deletions=deletions,
            patch="\n".join(lines),
        )


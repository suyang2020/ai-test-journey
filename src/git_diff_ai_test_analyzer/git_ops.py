from __future__ import annotations

import subprocess


class GitError(Exception):
    """Raised when a git operation fails."""


def check_git_available() -> bool:
    try:
        subprocess.run(
            ["git", "--version"],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def git_diff_branches(base: str, target: str) -> str:
    """Return diff between base and target branches (triple-dot)."""
    if not check_git_available():
        raise GitError(
            "git command not found. Install git and ensure it is on PATH."
        )

    cmd = ["git", "diff", f"{base}...{target}"]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise GitError(
            f"git diff failed between '{base}' and '{target}': {e.stderr.strip()}"
        ) from e
    return result.stdout


def git_diff_range(range_str: str) -> str:
    """Return diff for a commit range like HEAD~3..HEAD."""
    if not check_git_available():
        raise GitError(
            "git command not found. Install git and ensure it is on PATH."
        )

    cmd = ["git", "diff", range_str]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise GitError(
            f"git diff failed for range '{range_str}': {e.stderr.strip()}"
        ) from e
    return result.stdout

"""Detect planning documentation drift.

Compare VERIFICATION.md status (ground truth — phase actually delivered) against
ROADMAP.md / REQUIREMENTS.md markers (documentary claims). Warn on mismatch.

Exit 0 always (advisory). Print findings to stderr. Designed to be wired into
a git pre-commit hook on .planning/ changes, but also runnable standalone.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLANNING = ROOT / ".planning"
PHASES_DIR = PLANNING / "phases"
ROADMAP = PLANNING / "ROADMAP.md"
REQUIREMENTS = PLANNING / "REQUIREMENTS.md"

COMPLETE_STATUSES = {"complete", "passed"}


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        m = re.match(r"^(\w+):\s*(.+?)\s*$", line)
        if m:
            fields[m.group(1)] = m.group(2)
    return fields


def find_completed_phases() -> dict[str, Path]:
    """Return {phase_number: verification_path} for phases marked complete/passed."""
    completed: dict[str, Path] = {}
    for vfile in PHASES_DIR.glob("*/[0-9]*-VERIFICATION.md"):
        fm = parse_frontmatter(vfile)
        status = fm.get("status", "").strip().lower()
        if status not in COMPLETE_STATUSES:
            continue
        # Extract phase number from filename prefix (e.g. "15-VERIFICATION.md" → "15")
        m = re.match(r"^(\d+(?:\.\d+)?)-VERIFICATION\.md$", vfile.name)
        if m:
            completed[m.group(1)] = vfile
    return completed


def check_roadmap_checkbox(phase_num: str, roadmap_text: str) -> str | None:
    """Return error message if checkbox for phase is unchecked, else None."""
    pattern = re.compile(
        rf"^- \[( |x)\] \*\*Phase {re.escape(phase_num)}:", re.MULTILINE
    )
    match = pattern.search(roadmap_text)
    if not match:
        return f"ROADMAP.md: no checkbox line for Phase {phase_num}"
    if match.group(1) == " ":
        return f"ROADMAP.md: Phase {phase_num} checkbox is [ ] but VERIFICATION.md says complete"
    return None


def check_roadmap_progress_table(phase_num: str, roadmap_text: str) -> str | None:
    """Return error message if progress table row says Planned/In progress, else None."""
    pattern = re.compile(
        rf"^\|\s*{re.escape(phase_num)}\.\s.*?\|.*?\|\s*(\d+)/(\d+)\s*\|\s*([^|]+?)\s*\|",
        re.MULTILINE,
    )
    match = pattern.search(roadmap_text)
    if not match:
        return None  # progress table is optional
    done, total, status = match.group(1), match.group(2), match.group(3).strip()
    if "Complete" not in status and "complete" not in status:
        return (
            f"ROADMAP.md progress table: Phase {phase_num} status is "
            f"'{status}' ({done}/{total}) but VERIFICATION.md says complete"
        )
    return None


def find_phase_requirements(phase_num: str, req_text: str) -> list[str]:
    """Return list of REQ-IDs whose traceability table maps them to this phase."""
    req_ids: list[str] = []
    pattern = re.compile(
        rf"^\|\s*([A-Z][A-Z0-9-]+?)\s*\|\s*Phase {re.escape(phase_num)}\s*\|",
        re.MULTILINE,
    )
    for m in pattern.finditer(req_text):
        req_ids.append(m.group(1))
    return req_ids


def check_requirement_status(req_id: str, req_text: str) -> str | None:
    """Return error if REQ-ID is checklisted unchecked or table-marked Pending, else None."""
    issues: list[str] = []
    checkbox_pattern = re.compile(
        rf"^- \[( |x)\] \*\*{re.escape(req_id)}\*\*", re.MULTILINE
    )
    cb = checkbox_pattern.search(req_text)
    if cb and cb.group(1) == " ":
        issues.append(f"checklist [ ]")
    table_pattern = re.compile(
        rf"^\|\s*{re.escape(req_id)}\s*\|\s*Phase[^|]+\|\s*([^|]+?)\s*\|",
        re.MULTILINE,
    )
    tb = table_pattern.search(req_text)
    if tb:
        status = tb.group(1).strip()
        if "Complete" not in status and "Done" not in status and "✓" not in status:
            issues.append(f"traceability table '{status}'")
    if issues:
        return f"{req_id}: " + " + ".join(issues)
    return None


def main() -> int:
    if not ROADMAP.exists() or not REQUIREMENTS.exists() or not PHASES_DIR.exists():
        return 0  # nothing to check
    roadmap_text = ROADMAP.read_text(encoding="utf-8")
    req_text = REQUIREMENTS.read_text(encoding="utf-8")
    completed = find_completed_phases()
    if not completed:
        return 0

    findings: list[str] = []
    for phase_num, vfile in sorted(completed.items(), key=lambda kv: float(kv[0])):
        for issue in (
            check_roadmap_checkbox(phase_num, roadmap_text),
            check_roadmap_progress_table(phase_num, roadmap_text),
        ):
            if issue:
                findings.append(f"  Phase {phase_num} [{vfile.relative_to(ROOT)}]: {issue}")
        for req_id in find_phase_requirements(phase_num, req_text):
            issue = check_requirement_status(req_id, req_text)
            if issue:
                findings.append(f"  Phase {phase_num}: REQUIREMENTS.md drift — {issue}")

    if findings:
        sys.stderr.write(
            "\n⚠ Planning documentation drift detected\n"
            "  (VERIFICATION.md says complete but markers say otherwise)\n\n"
        )
        for f in findings:
            sys.stderr.write(f + "\n")
        sys.stderr.write(
            "\n  Fix manually: edit ROADMAP.md / REQUIREMENTS.md to match VERIFICATION.md.\n"
            "  This check is advisory — commit will proceed.\n\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

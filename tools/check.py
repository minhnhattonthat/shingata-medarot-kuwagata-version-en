"""check.py: the repo's one-command check (tests + text lint). The pre-commit hook runs it.

Runs pytest over tests/ (fast tests only; mark emulator tests with @pytest.mark.slow), then tools/lint.py (English
text against the box budgets in data/windows.json). Exit code is nonzero if either fails.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    args = [sys.executable, "-X", "utf8", "-m", "pytest", "-q", "-m", "not slow", str(ROOT / "tests")]
    rc = subprocess.call(args, cwd=ROOT)
    # width-gate lint of the English script (tools/lint.py, budgets in data/windows.json)
    lint_rc = subprocess.call([sys.executable, "-X", "utf8", str(ROOT / "tools" / "lint.py"), "-q"], cwd=ROOT)
    sys.exit(rc or lint_rc)

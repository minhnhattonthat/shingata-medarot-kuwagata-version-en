"""check.py: the repo's one-command check (tests + text lint). The pre-commit hook runs it.

Runs pytest over tests/ (fast tests only; mark emulator tests with @pytest.mark.slow). Exit code is pytest's.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    args = [sys.executable, "-X", "utf8", "-m", "pytest", "-q", "-m", "not slow", str(ROOT / "tests")]
    sys.exit(subprocess.call(args, cwd=ROOT))

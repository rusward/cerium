"""Shared helpers for the Hydrogen test suite."""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
EXAMPLES = os.path.join(ROOT, "examples")

if SRC not in sys.path:
    sys.path.insert(0, SRC)


def run_cli(*args, cwd=None):
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = SRC + (os.pathsep + existing if existing else "")
    return subprocess.run(
        [sys.executable, "-m", "hydrogenc", *args],
        cwd=cwd or ROOT,
        env=env,
        capture_output=True,
        text=True,
    )


cli = run_cli


def write(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def read(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()

"""Shared helpers for the Cerium test suite."""

import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
EXAMPLES = os.path.join(ROOT, "examples")

if SRC not in sys.path:
    sys.path.insert(0, SRC)


def find_c_compiler():
    configured = os.environ.get("CC")
    if configured:
        return configured

    if sys.platform == "darwin":
        candidates = ("clang", "gcc", "cc")
    else:
        candidates = ("gcc", "clang", "cc")

    for candidate in candidates:
        path = shutil.which(candidate)
        if path:
            return path
    return None


def binary_path(directory, stem):
    suffix = ".exe" if os.name == "nt" else ""
    return os.path.join(directory, stem + suffix)


def run_cli(*args, cwd=None):
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = SRC + (os.pathsep + existing if existing else "")
    return subprocess.run(
        [sys.executable, "-m", "ceriumc", *args],
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

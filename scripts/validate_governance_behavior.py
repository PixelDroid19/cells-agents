#!/usr/bin/env python3
"""Run actual work-routing and command-policy regressions, not prose substring checks."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
if __name__ == "__main__":
    suite = unittest.TestSuite()
    for name in ("test_workflow.py", "test_runtime.py"):
        suite.addTests(unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern=name))
    raise SystemExit(not unittest.TextTestRunner(verbosity=1).run(suite).wasSuccessful())

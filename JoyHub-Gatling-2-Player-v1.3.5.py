#!/usr/bin/env python3
"""Compatibility launcher for JoyHub Gatling 2 Player v1.3.5."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from joyhub_gatling2.main import main

if __name__ == "__main__":
    raise SystemExit(main())

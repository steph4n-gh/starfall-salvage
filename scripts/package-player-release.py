#!/usr/bin/env python3
"""Synchronize the reviewed player ZIP and site copies through one workflow.

Equivalent to `python3 scripts/sync-release.py sync`. No approval or publishing
is performed. An intact reviewed ZIP is reused across Python/zlib versions.
"""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("sync-release.py")))["main"](["sync"])

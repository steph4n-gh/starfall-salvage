#!/usr/bin/env python3
"""Repackage the checked-in, verified 1.1 player files without changing them.

Run: python3 scripts/package-player-release.py
Requires Python 3's standard library only. This does not compile the game,
regenerate the PDF, publish a release, or read any external project folder.
The player files are frozen inputs; change their reviewed release version
and verification constants deliberately when preparing a new game release.
"""

import hashlib
import json
import os
from pathlib import Path
import tempfile
import zipfile
import zlib


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "release/player-v1.1"
OUTPUT = ROOT / "release/starfall-salvage-1.1-player.zip"
EXPECTED_ZIP = "dab86c9eec9a9524a2381094044b646cfb1fa6a1f625c4424a242f94d504ac22"
EXPECTED_ROM = "105e410008ceb8dd2d6c83aebb033972b8cfcfeb41a714fcc7f260966ba193db"
EXPECTED_PDF = "794a4305f70a7e9cd54eb6b183dfd5a4ea6d6a03c7b476ef99ef827e407565fd"
FILES = {
    "CREDITS.txt", "INSTRUCTIONS.pdf", "LICENSE", "QUICK-START.txt",
    "READ-ME.txt", "RELEASE-NOTES.txt", "SHA256SUMS.txt",
    "Starfall-Salvage-1.1.gbc",
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    if {p.name for p in INPUT.iterdir()} != FILES:
        raise SystemExit("Frozen player directory does not match the eight-file allowlist.")
    if any(not p.is_file() or p.is_symlink() for p in INPUT.iterdir()):
        raise SystemExit("Player payload must contain ordinary files only.")
    payload = {name: (INPUT / name).read_bytes() for name in sorted(FILES)}
    hashes = {name: sha256(data) for name, data in payload.items()}
    if hashes["Starfall-Salvage-1.1.gbc"] != EXPECTED_ROM:
        raise SystemExit("ROM does not match the verified 1.1 release.")
    if hashes["INSTRUCTIONS.pdf"] != EXPECTED_PDF:
        raise SystemExit("PDF does not match the reviewed 14-page manual.")
    manifest = {}
    for row in payload["SHA256SUMS.txt"].decode("ascii").splitlines():
        expected, name = row.split("  ", 1)
        if name in manifest:
            raise SystemExit("Duplicate checksum manifest entry.")
        manifest[name] = expected
    if manifest != {name: digest for name, digest in hashes.items() if name != "SHA256SUMS.txt"}:
        raise SystemExit("Player checksum manifest does not match the frozen payload.")

    handle, temp_name = tempfile.mkstemp(prefix=".player-archive-", suffix=".zip", dir=OUTPUT.parent)
    os.close(handle)
    staged = Path(temp_name)
    try:
        with zipfile.ZipFile(staged, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name, data in payload.items():
                info = zipfile.ZipInfo("Starfall-Salvage-1.1/" + name, date_time=(2026, 10, 14, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        with zipfile.ZipFile(staged) as archive:
            if archive.testzip() is not None:
                raise SystemExit("Rebuilt ZIP failed its CRC check.")
            expected_names = ["Starfall-Salvage-1.1/" + name for name in payload]
            if archive.namelist() != expected_names:
                raise SystemExit("Rebuilt ZIP has unexpected entries.")
            for name, data in payload.items():
                if archive.read("Starfall-Salvage-1.1/" + name) != data:
                    raise SystemExit("Rebuilt ZIP has an altered payload.")
        archive_hash = sha256(staged.read_bytes())
        if archive_hash != EXPECTED_ZIP:
            raise SystemExit(
                "Rebuilt ZIP differs from the approved archive; no output replaced. "
                "Review the payload and Python/zlib compression version before updating the release."
            )
        if any((INPUT / name).read_bytes() != data for name, data in payload.items()):
            raise SystemExit("Player inputs changed during packaging; no output replaced.")
        staged.chmod(0o644)
        staged.replace(OUTPUT)
    finally:
        staged.unlink(missing_ok=True)

    print(json.dumps({
        "status": "local-draft-not-published",
        "input_payload": {"directory": "release/player-v1.1", "file_count": len(payload), "sha256": hashes},
        "input_payload_unchanged": True,
        "archive": {"path": str(OUTPUT.relative_to(ROOT)), "bytes": OUTPUT.stat().st_size, "sha256": archive_hash},
        "matches_approved_archive": True,
        "checksum_manifest_passed": True,
        "zip_crc_and_payload_passed": True,
        "zlib_version": zlib.ZLIB_RUNTIME_VERSION,
    }, indent=2))


if __name__ == "__main__":
    main()

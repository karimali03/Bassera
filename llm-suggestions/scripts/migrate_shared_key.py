#!/usr/bin/env python3
"""
Copy OPENROUTER_API_KEY -> SERVICE_API_KEY in .env safely.
Usage:
    python scripts/migrate_shared_key.py [--env .env] [--force] [--dry-run]

Behavior:
- Reads the specified env file (defaults to .env)
- If SERVICE_API_KEY is present and --force not provided, exits without changes
- If OPENROUTER_API_KEY present and SERVICE_API_KEY missing, copies value into SERVICE_API_KEY
- Sets ALLOW_SHARED_API_KEY=true so the shared-key mode is explicit
- Backs up original env to .env.bak.TIMESTAMP before writing
"""

from __future__ import annotations

import argparse
import datetime
import shutil
import sys
from pathlib import Path


def load_env(path: Path) -> dict:
    data = {}
    if not path.exists():
        return data
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        data[key.strip()] = val.strip()
    return data


def write_env(path: Path, data: dict) -> None:
    lines = []
    for k, v in data.items():
        lines.append(f"{k}={v}")
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default=".env", help="Path to env file to modify")
    parser.add_argument("--force", action="store_true", help="Overwrite SERVICE_API_KEY if present")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing")
    args = parser.parse_args()

    env_path = Path(args.env)
    if not env_path.exists():
        print(f"Env file {env_path} not found.")
        return 2

    data = load_env(env_path)
    open_key = data.get("OPENROUTER_API_KEY")
    service_key = data.get("SERVICE_API_KEY")

    if not open_key:
        print("OPENROUTER_API_KEY not found in", env_path)
        return 3

    if service_key and not args.force:
        print("SERVICE_API_KEY already present. Use --force to overwrite.")
        return 0

    print(f"Will set SERVICE_API_KEY to the value of OPENROUTER_API_KEY in {env_path}")
    if args.dry_run:
        return 0

    # Backup
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    backup = env_path.with_suffix(env_path.suffix + f".bak.{timestamp}")
    shutil.copy2(env_path, backup)
    print(f"Backed up original to {backup}")

    data["SERVICE_API_KEY"] = open_key
    data["ALLOW_SHARED_API_KEY"] = "true"

    write_env(env_path, data)
    print(f"Wrote SERVICE_API_KEY into {env_path}")
    print(f"Enabled ALLOW_SHARED_API_KEY in {env_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

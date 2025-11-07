import argparse
import datetime as dt
import json
import os
import pathlib
import re
import shutil
import sys
from typing import Any, Dict, List, Optional

import requests

from odoo_jsonrpc import OdooClient


def timestamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_dir(path: pathlib.Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def list_databases(url: str) -> List[str]:
    client = OdooClient(url)
    dbs = client.list_databases() or []
    if isinstance(dbs, dict) and dbs.get("databases"):
        dbs = dbs["databases"]
    return list(dbs)


def backup_db(url: str, master_pwd: str, db: str, outdir: pathlib.Path, fmt: str = "zip") -> pathlib.Path:
    base = url.rstrip('/')
    s = requests.Session()
    s.get(f"{base}/web", timeout=30)
    csrf = s.cookies.get('csrf_token') or ""

    payload = {
        "backup_db": db,
        "backup_format": fmt,  # 'zip' includes filestore; 'dump' is SQL only
        "master_pwd": master_pwd,
        "csrf_token": csrf,
    }
    resp = s.post(f"{base}/web/database/backup", data=payload, timeout=600, stream=True)
    resp.raise_for_status()
    # Content-Disposition may include filename; otherwise generate
    fname = None
    cd = resp.headers.get("Content-Disposition", "")
    m = re.search(r"filename=\"?([^\";]+)\"?", cd)
    if m:
        fname = m.group(1)
    if not fname:
        fname = f"{db}_{timestamp()}.{fmt}"
    out_path = outdir / fname
    with open(out_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
    return out_path


def zip_workspace(root: pathlib.Path, outdir: pathlib.Path, name: Optional[str] = None) -> pathlib.Path:
    """Zip key project folders and configs for full backup."""
    ts = timestamp()
    base_name = name or f"workspace_{ts}"
    archive_path = outdir / f"{base_name}.zip"
    # Build inclusion list
    include_patterns = [
        "pos_beverage_modifier/",
        "odoo19-shadow/addons/",
        "odoo19-shadow/docker-compose.yml",
        "odoo19-shadow/docker-compose.fixed.yml",
        "odoo19-shadow/docker-compose.dp002.yml",
        "nginx_*.conf",
        "main_items.json",
        "main_items.csv",
        "menu_payload_m*.json",
        "requirements.txt",
        "*.py",
        "*.md",
        "*.xml",
        "*.json",
        "*.csv",
    ]

    def should_include(p: pathlib.Path) -> bool:
        rel = p.relative_to(root).as_posix()
        # exclude backups directory itself to avoid recursion
        if rel.startswith("backups/"):
            return False
        for pat in include_patterns:
            if pat.endswith("/"):
                if rel.startswith(pat.rstrip("/")):
                    return True
            elif pat.startswith("nginx_") and pat.endswith(".conf"):
                if rel.startswith("nginx_") and rel.endswith(".conf"):
                    return True
            elif pat.startswith("menu_payload_m") and pat.endswith(".json"):
                if rel.startswith("menu_payload_m") and rel.endswith(".json"):
                    return True
            elif pat.startswith("*"):
                if rel.endswith(pat.lstrip("*")):
                    return True
            else:
                if rel == pat:
                    return True
        return False

    import zipfile

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for p in root.rglob("*"):
            if p.is_file() and should_include(p):
                arcname = p.relative_to(root).as_posix()
                zipf.write(p, arcname)
    return archive_path


def main():
    ap = argparse.ArgumentParser(description="Create full backup: Odoo DB zip + workspace archive + manifest")
    ap.add_argument("--url", default="http://127.0.0.1:18069")
    ap.add_argument("--master", default="odoo", help="Odoo master password (ADMIN_PASSWORD)")
    ap.add_argument("--db", action="append", help="Database name to backup (can repeat). If omitted, backup all")
    ap.add_argument("--out", default="backups", help="Output directory for backups")
    ap.add_argument("--skip-workspace", action="store_true", help="Skip zipping workspace files")
    ap.add_argument("--only-workspace", action="store_true", help="Only zip workspace, skip DB backup")
    ap.add_argument("--only-db", action="store_true", help="Only backup DBs, skip workspace zip")
    ap.add_argument("--format", choices=["zip", "dump"], default="zip", help="Backup format for DB")
    args = ap.parse_args()

    outdir = pathlib.Path(args.out)
    ensure_dir(outdir)

    artifacts: Dict[str, Any] = {"timestamp": timestamp(), "url": args.url, "db_format": args.format, "databases": [], "workspace": None}

    # Backup each database
    if not args.only_workspace:
        dbs = args.db or list_databases(args.url)
        if not dbs:
            raise RuntimeError("No databases found to backup")
        for db in dbs:
            path = backup_db(args.url, args.master, db, outdir, args.format)
            size = path.stat().st_size if path.exists() else 0
            artifacts["databases"].append({"db": db, "file": str(path), "size": size})

    # Zip workspace
    if not args.skip_workspace and not args.only_db:
        workspace_root = pathlib.Path.cwd()
        wsp = zip_workspace(workspace_root, outdir)
        artifacts["workspace"] = {"file": str(wsp), "size": wsp.stat().st_size}

    # Write manifest
    manifest_path = outdir / f"backup_manifest_{timestamp()}.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(artifacts, f, ensure_ascii=False, indent=2)

    print(json.dumps({"status": "ok", "manifest": str(manifest_path), "artifacts": artifacts}, ensure_ascii=False))


if __name__ == "__main__":
    main()

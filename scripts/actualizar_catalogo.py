#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from catalog.config import DATA_DIR, load_configs, load_json, write_json
from catalog.processing import build_public_catalog


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Actualiza el catálogo público INGALITO desde KOI."
    )
    parser.add_argument(
        "--skip-scrape",
        action="store_true",
        help="Procesa data/koi_raw.json existente sin llamar a Scrapy.",
    )
    parser.add_argument(
        "--raw",
        type=Path,
        help="Usa un JSON RAW alternativo, útil para pruebas.",
    )
    return parser.parse_args()


def run_scraper(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "scrapy",
        "crawl",
        "koi",
        "-O",
        str(output_path),
        "--loglevel",
        "INFO",
    ]
    subprocess.run(command, check=True)


def main() -> int:
    args = parse_args()
    catalog_config, margins, prices_config = load_configs()
    raw_path = args.raw or DATA_DIR / "koi_raw.json"
    previous_raw_path = DATA_DIR / "koi_raw.previous.json"
    next_raw_path = DATA_DIR / "koi_raw.next.json"
    catalog_path = DATA_DIR / "catalogo.json"
    history_path = DATA_DIR / "historial.json"

    previous_raw = load_json(raw_path) if raw_path.exists() else []
    previous_catalog = load_json(catalog_path) if catalog_path.exists() else None

    if args.skip_scrape:
        current_raw_path = raw_path
    else:
        if raw_path.exists():
            shutil.copyfile(raw_path, previous_raw_path)
        if next_raw_path.exists():
            next_raw_path.unlink()
        run_scraper(next_raw_path)
        current_raw_path = next_raw_path

    current_raw = load_json(current_raw_path)
    catalog, events, stats = build_public_catalog(
        current_raw,
        previous_raw,
        catalog_config,
        margins,
        prices_config,
        previous_catalog,
    )

    if not args.skip_scrape:
        next_raw_path.replace(raw_path)
    if events:
        history = load_json(history_path) if history_path.exists() else []
        write_json(history_path, history + events)
    write_json(catalog_path, catalog)

    print("Resumen de actualización")
    for key, value in stats.items():
        print(f"- {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
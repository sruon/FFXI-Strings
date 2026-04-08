#!/usr/bin/env python3

import multiprocessing as mp
import os
import re
from pathlib import Path

import yaml
from loguru import logger

from parser.stringdat import StringDatParser
from parser.string_formatter import format_string

ZONE_NAME_FIXES = {
    " ": "_", "'": "", "#": "",
    "_-_": "-", "[U]": "U",
    "-LegionA": "-Legion_A", "-LegionB": "-Legion_B",
    "Escha-": "Escha_", "Desuetia-Empyreal": "Desuetia_Empyreal",
}


def sanitize_zone_name(name):
    for old, new in ZONE_NAME_FIXES.items():
        name = name.replace(old, new)
    return name


def slugify(text):
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"[^a-zA-Z0-9 ]", " ", text).strip()
    words = text.upper().split()[:8]
    if not words:
        return None
    slug = "_".join(words)
    return slug if slug[0].isalpha() else f"ID_{slug}"


def dump_zone(zone):
    files = zone.get("files", {})
    strings_path = files.get("strings_na")
    if not strings_path:
        return

    ffxi_path = Path(os.environ.get("FFXI_PATH", r"C:\Program Files (x86)\PlayOnline\SquareEnix\FINAL FANTASY XI"))
    full_path = ffxi_path / strings_path
    if not full_path.exists():
        return

    try:
        parsed = StringDatParser.parse_file_english(full_path)
    except Exception as e:
        logger.error(f"Failed to parse {zone['name']}: {e}")
        return

    entries = []
    seen = {}
    max_len = 0

    for s in parsed.strings:
        text = format_string(s.text)
        if len(text) <= 1:
            continue

        slug = slugify(text) or f"ID_{s.index}"
        if slug in seen:
            seen[slug] += 1
            slug = f"{slug}_{seen[slug]}"
        else:
            seen[slug] = 1

        max_len = max(max_len, len(slug))
        entries.append((slug, s.index, text))

    if not entries:
        return

    out_dir = Path("dumps") / sanitize_zone_name(zone["name"])
    out_dir.mkdir(parents=True, exist_ok=True)

    with (out_dir / "Text.lua").open("w", encoding="utf-8") as f:
        f.write("    text =\n    {\n")
        for slug, index, comment in entries:
            f.write(f"        {slug.ljust(max_len)} = {index},  -- {comment}\n")
        f.write("    },\n")

    logger.info(f"{zone['name']}: {len(entries)} strings")


def main():
    with open("data/zones.yaml") as f:
        zones = yaml.safe_load(f)["zones"]

    Path("dumps").mkdir(parents=True, exist_ok=True)
    with mp.Pool(os.cpu_count() or 4) as pool:
        pool.map(dump_zone, zones)


if __name__ == "__main__":
    main()

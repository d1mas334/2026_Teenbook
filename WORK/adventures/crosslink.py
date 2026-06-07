#!/usr/bin/env python3
"""
Скрипт для расстановки перекрёстных ссылок [text](path/concept.md)
в markdown-файлах раздела «Я и мои приключения».

Структура:
  WEB/adventures/<block>/
    concepts/<concept>.md

Понятия загружаются из WORK/adventures/<block>/concepts.json.
Ссылки ведут на concepts/ относительно файла или в другой блок.
"""

import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
WEB_DIR = BASE / "WEB" / "adventures"
WORK_DIR = BASE / "WORK" / "adventures"

# Блок для каждого понятия определяется по папке, в которой лежит concepts.json
CONCEPT_BLOCK: dict[str, str] = {}


def load_concepts(work_dir: Path) -> list[dict]:
    concepts = []
    for block_dir in sorted(work_dir.iterdir()):
        if not block_dir.is_dir():
            continue
        json_path = block_dir / "concepts.json"
        if not json_path.exists():
            continue
        with open(json_path, encoding="utf-8") as f:
            block_concepts = json.load(f)["concepts"]
        for c in block_concepts:
            cid = c["file"].replace(".md", "")
            CONCEPT_BLOCK[cid] = block_dir.name
            c["id"] = cid
            concepts.append(c)
    return concepts


def build_patterns(concepts: list[dict]) -> list[tuple[str, str, re.Pattern]]:
    patterns = []
    for c in concepts:
        cid = c["id"]
        name = c["name"]
        candidates = [name] + c.get("aliases", [])
        candidates = sorted(set(candidates), key=lambda x: -len(x))
        escaped = [re.escape(w) for w in candidates]
        pattern = r"(?<!\w)(" + "|".join(escaped) + r")(?!\w)"
        patterns.append((cid, name, re.compile(pattern)))
    return patterns


# ─── pymorphy2 (опционально) ────────────────────────────────────────────────
try:
    import pymorphy2
    MORPH = pymorphy2.MorphAnalyzer()
    HAS_MORPH = True
except ImportError:
    HAS_MORPH = False


# ─── Зоны пропуска ───────────────────────────────────────────────────────────
def skip_zones(text: str) -> list[tuple[int, int]]:
    zones = []
    for m in re.finditer(r"\[\[.*?\]\]", text):
        zones.append((m.start(), m.end()))
    for m in re.finditer(r"```.*?```", text, re.DOTALL):
        zones.append((m.start(), m.end()))
    for m in re.finditer(r"`[^`]+`", text):
        zones.append((m.start(), m.end()))
    for m in re.finditer(r"\[[^\]]*\]\([^)]+\)", text):
        zones.append((m.start(), m.end()))
    for m in re.finditer(r"^#.+$", text, re.MULTILINE):
        zones.append((m.start(), m.end()))
    return _merge(sorted(zones))


def _merge(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not spans:
        return []
    spans.sort()
    merged = [spans[0]]
    for s in spans[1:]:
        if s[0] <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], s[1]))
        else:
            merged.append(s)
    return merged


def in_zones(pos: int, zones: list[tuple[int, int]]) -> bool:
    for start, end in zones:
        if start <= pos < end:
            return True
        if pos < start:
            return False
    return False


# ─── Определение контекста файла ─────────────────────────────────────────────
def resolve_path_to_concept(filepath: Path, target_cid: str) -> str:
    """
    Вычисляет относительный путь от filepath к concepts/target_cid.md
    с учётом структуры: <block>/concepts/<cid>.md
    """
    target_block = CONCEPT_BLOCK.get(target_cid)
    if not target_block:
        return f"concepts/{target_cid}.md"  # fallback

    # Определяем блок и тип файла
    parts = filepath.resolve().relative_to(WEB_DIR.resolve()).parts
    # parts[0] = block name, parts[1] = "concepts" or article name
    source_block = parts[0]
    is_concept_file = len(parts) > 1 and parts[1] == "concepts"

    if source_block == target_block:
        # Оба в одном блоке
        if is_concept_file:
            return f"{target_cid}.md"
        else:
            return f"concepts/{target_cid}.md"
    else:
        # Разные блоки — поднимаемся на уровень выше
        prefix = "../" if is_concept_file else "../"
        return f"{prefix}{target_block}/concepts/{target_cid}.md"


# ─── Обработка файла ─────────────────────────────────────────────────────────
def process_file(filepath: Path, patterns: list[tuple]) -> int:
    text = filepath.read_text(encoding="utf-8")
    zones = skip_zones(text)

    all_matches = []
    for cid, name, pat in patterns:
        for m in pat.finditer(text):
            all_matches.append((m.start(), m.end(), m.group(1), cid))

    all_matches.sort(key=lambda x: x[0])

    filtered = []
    last_end = 0
    for start, end, matched_text, cid in all_matches:
        if start < last_end:
            continue
        if in_zones(start, zones):
            continue
        # Не ссылаемся сами на себя (когда concept-файл упоминает своё же имя)
        if str(filepath).endswith(f"concepts/{cid}.md"):
            continue
        filtered.append((start, end, matched_text, cid))
        last_end = end

    if not filtered:
        return 0

    for start, end, matched_text, cid in reversed(filtered):
        href = resolve_path_to_concept(filepath, cid)
        link = f"[{matched_text}]({href})"
        text = text[:start] + link + text[end:]

    filepath.write_text(text, encoding="utf-8")
    return len(filtered)


# ─── Главная ─────────────────────────────────────────────────────────────────
def main():
    concepts = load_concepts(WORK_DIR)
    patterns = build_patterns(concepts)

    print(f"Понятий: {len(concepts)}")
    print(f"Падежный матчинг: {'pymorphy2' if HAS_MORPH else 'только алиасы'}")
    print()

    total = 0
    for fp in sorted(WEB_DIR.rglob("*.md")):
        count = process_file(fp, patterns)
        symbol = "✓" if count else "—"
        print(f"  {symbol} {fp.relative_to(WEB_DIR)}: {count}")
        total += count

    print(f"\nИтого: {total} замен")


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
import os
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
WORK_ROOT = REPO_ROOT / "WORK" / "me_and_state"
WEB_ROOT = REPO_ROOT / "WEB" / "me_and_state"
LINK_TARGETS_PATH = WORK_ROOT / "link_targets.json"

HEADER_RE = re.compile(r"^\s{0,3}#{1,6}\s")
PROTECTED_RE = re.compile(r"(`[^`\n]+`|!?\[[^\]]+\]\([^)]+\)|<https?://[^>]+>)")


def load_targets() -> list[dict]:
  data = json.loads(LINK_TARGETS_PATH.read_text(encoding="utf-8"))
  targets = []
  for item in data["targets"]:
    aliases = {item["title"], *item.get("aliases", [])}
    targets.append({
      "title": item["title"],
      "target": (REPO_ROOT / item["target"]).resolve(),
      "aliases": sorted((alias for alias in aliases if alias), key=len, reverse=True),
    })
  return sorted(targets, key=lambda item: len(item["title"]), reverse=True)


def build_pattern(alias: str) -> re.Pattern:
  escaped = re.escape(alias)
  return re.compile(rf"(?<![\wА-Яа-яЁё-])({escaped})(?![\wА-Яа-яЁё-])", re.IGNORECASE)


def link_plain_part(part: str, alias: str, rel_link: str) -> tuple[str, bool]:
  pattern = build_pattern(alias)

  def replace(match: re.Match) -> str:
    return f"[{match.group(1)}]({rel_link})"

  updated, count = pattern.subn(replace, part, count=1)
  return updated, count > 0


def link_line(line: str, target: dict, rel_link: str) -> tuple[str, bool]:
  parts = PROTECTED_RE.split(line)
  for idx, part in enumerate(parts):
    if idx % 2 == 1:
      continue
    for alias in target["aliases"]:
      updated, changed = link_plain_part(part, alias, rel_link)
      if changed:
        parts[idx] = updated
        return "".join(parts), True
  return line, False


def process_file(md_path: Path, targets: list[dict]) -> bool:
  original = md_path.read_text(encoding="utf-8")
  lines = original.splitlines()
  updated_lines = []
  in_code = False
  linked_titles: set[str] = set()

  for line in lines:
    if line.strip().startswith("```"):
      in_code = not in_code
      updated_lines.append(line)
      continue

    if in_code or HEADER_RE.match(line):
      updated_lines.append(line)
      continue

    updated_line = line
    for target in targets:
      if target["title"] in linked_titles:
        continue
      if target["target"] == md_path.resolve():
        continue
      if not target["target"].exists():
        continue

      rel_link = os.path.relpath(target["target"], start=md_path.parent).replace("\\", "/")
      new_line, changed = link_line(updated_line, target, rel_link)
      if changed:
        updated_line = new_line
        linked_titles.add(target["title"])

    updated_lines.append(updated_line)

  updated = "\n".join(updated_lines) + "\n"
  if updated != original:
    md_path.write_text(updated, encoding="utf-8")
    return True
  return False


def main() -> None:
  targets = load_targets()
  changed = 0
  files = sorted(WEB_ROOT.rglob("*.md"))
  for md_path in files:
    if process_file(md_path, targets):
      changed += 1
      print(f"updated: {md_path.relative_to(REPO_ROOT)}")
  print(f"Готово: обработано файлов {len(files)}, изменено {changed}.")


if __name__ == "__main__":
  main()

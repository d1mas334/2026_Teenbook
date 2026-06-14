import json
import pathlib
import time
import requests


SEARCH_TERMS = [
  "паспорт гражданина Российской Федерации",
  "СНИЛС",
  "идентификационный номер налогоплательщика",
  "обязательное медицинское страхование",
  "регистрационный учёт граждан Российской Федерации",
  "персональные данные",
  "Госуслуги",
  "документ, удостоверяющий личность",
]

URL = "https://www.wikidata.org/w/api.php"


def search_entities(term: str, limit: int = 5) -> list[dict]:
  headers = {
    "Accept": "application/json",
    "User-Agent": "teenbook-me-and-state/1.0 (educational project)",
  }
  params = {
    "action": "wbsearchentities",
    "format": "json",
    "language": "ru",
    "uselang": "ru",
    "search": term,
    "limit": limit,
  }

  response = requests.get(URL, params=params, headers=headers, timeout=30)
  if response.status_code == 429:
    time.sleep(5)
    response = requests.get(URL, params=params, headers=headers, timeout=30)
  response.raise_for_status()
  return response.json().get("search", [])


def build_export() -> dict:
  concepts = []
  for term in SEARCH_TERMS:
    matches = search_entities(term)
    concepts.append({
      "search_term": term,
      "matches": [
        {
          "id": item.get("id", ""),
          "label": item.get("label", ""),
          "description": item.get("description", ""),
          "url": item.get("concepturi", ""),
        }
        for item in matches
      ],
    })
    time.sleep(1)

  return {
    "project": "Я и государство: Мои документы",
    "source": "Wikidata Entity Search API",
    "concepts": concepts,
  }


def save_result(data: dict, output_path: pathlib.Path) -> None:
  output_path.parent.mkdir(parents=True, exist_ok=True)
  with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)


def main() -> None:
  script_dir = pathlib.Path(__file__).resolve().parent
  output_path = script_dir.parent / "data" / "wikidata_export.json"

  data = build_export()
  save_result(data, output_path)
  print(f"Готово: результат сохранён в {output_path}")


if __name__ == "__main__":
  main()

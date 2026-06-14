# Раздел 11: Я и государство

Раздел посвящен тому, как подросток взаимодействует с государством в обычной жизни: через документы, школу, закон, полицию, медицину, Госуслуги, выборы, гражданство и совершеннолетие.

## Команда

- Попов Николай Александрович
- Копылов Максим Дмитриевич

## Цель раздела

Собрать структурированную базу знаний, которая:

- объясняет государственные и правовые темы простым языком
- показывает, где у подростка есть права и обязанности
- помогает ориентироваться в документах, учреждениях и цифровых сервисах
- использует данные Wikidata и JSON-выгрузки
- поддерживает диаграммы связей между понятиями

## Подразделы

| № | Подраздел | WORK | WEB |
|---|-----------|------|-----|
| 1 | Мои документы | `my_documents` | `../../WEB/me_and_state/my_documents/index.md` |
| 2 | Мои права и обязанности | `my_rights_and_responsibilities` | `../../WEB/me_and_state/my_rights_and_responsibilities/index.md` |
| 3 | Я и закон | `me_and_law` | `../../WEB/me_and_state/me_and_law/index.md` |
| 4 | Я и школа как часть государства | `school_as_part_of_state` | `../../WEB/me_and_state/school_as_part_of_state/index.md` |
| 5 | Я и полиция | `me_and_police` | `../../WEB/me_and_state/me_and_police/index.md` |
| 6 | Я и медицина | `me_and_medicine` | `../../WEB/me_and_state/me_and_medicine/index.md` |
| 7 | Я после 18 лет | `me_after_18_years_old` | `../../WEB/me_and_state/me_after_18_years_old/index.md` |
| 8 | Я и выборы | `me_and_election` | `../../WEB/me_and_state/me_and_election/index.md` |
| 9 | Я и Госуслуги | `me_and_gosuslugi` | `../../WEB/me_and_state/me_and_gosuslugi/index.md` |
| 10 | Я и гражданство | `me_and_citizenship` | `../../WEB/me_and_state/me_and_citizenship/index.md` |

## Структура подразделов

В каждой рабочей папке есть:

- `README.md` — описание темы и краткое содержание
- `concepts.json` — список внутренних тем
- `scripts/query.py` — сбор данных из Wikidata
- `data/wikidata_export.json` — результат выгрузки
- `images/` — диаграммы Mermaid и PNG-экспорты

## WEB

Публикуемая часть находится в:

- `WEB/me_and_state/index.md`
- `WEB/me_and_state/<subsection>/index.md`
- `WEB/me_and_state/<subsection>/concepts/*.md`

Markdown-страницы в `WEB` дают читателю короткий вход в тему, а файлы в `concepts/` являются отдельными статьями по каждому пункту из `concepts.json`.

## Перекрестные ссылки

Для раздела добавлена автоматическая перелинковка, как в других частях проекта:

- `concepts_all.json` — общий список всех понятий раздела
- `link_targets.json` — карта целей и алиасов для ссылок
- `scripts/insert_crosslinks.py` — скрипт, который расставляет ссылки в Markdown-статьях

Запуск:

```bash
python3 WORK/me_and_state/scripts/insert_crosslinks.py
```

Скрипт обрабатывает `WEB/me_and_state/**/*.md`, защищает уже существующие markdown-ссылки, заголовки и кодовые блоки, а затем вставляет ссылки на связанные статьи.

## Результат

Раздел можно использовать как готовый блок TeenBook: у него есть рабочие данные, диаграммы, Wikidata-выгрузки, web-страницы в Markdown-формате и сеть перекрестных ссылок между статьями.

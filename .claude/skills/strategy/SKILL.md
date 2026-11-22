---
name: strategy
description: Продуктовая и коммуникационная стратегии по выбранному варианту, план проверки, проверка согласованности и итоговый документ для руководителя. Использовать после выбора варианта в точке 3.
---

# Стратегия

Методика: `method/strategy.md`. Шаблоны: `method/templates/strategy-product.md`, `strategy-comms.md`, `validation.md`.

1. `sa.py log "strategist: стратегия" --start`. Вызови `strategist` с задачей «стратегия», выбором человека из точки 3 (есть в сводке `sa.py resume`), напоминанием закрыть каждый пункт «Критерия готовности» из брифа и путями к `brief.md`, `picture.md`, `options.md`, `claims.jsonl`. Он пишет `work/strategy-product.md`, `work/strategy-comms.md`, `work/validation.md`, расчёты в `work/calc/`.
2. `sa.py log --done A-n`, `sa.py check`.
3. `sa.py log "red-team: согласованность" --start`. Вызови `red-team` с задачей «согласованность» и путями к трём файлам стратегии и `options.md`. Найденное исправь сам, если правок немного, иначе верни `strategist` списком. `sa.py log --done A-n`.
4. `sa.py check` до нуля ошибок.
5. Собери `out/strategy.md` по разделу «Итоговый документ» из `method/strategy.md`. Если в «Критерии готовности» брифа человек задал свой состав документа, части и их порядок берутся оттуда. Метки утверждений сохрани. Это документ для руководителя: сначала вывод.
6. `sa.py report`, затем `sa.py check`.
7. Точка 4: `sa.py gate 4 waiting`. Покажи вывод в пяти строках и пути к `out/strategy.md` и `out/report.md`. Спроси: «Принимаете стратегию или что поправить?» Остановись. Правки человека: внеси, запиши `sa.py log "..." --actor human --kind исправление`, повтори `check` и `report`.
8. После принятия: `sa.py gate 4 passed --note "..."` и `sa.py step decision --next "Фиксация решения: скилл decision"`. Переходи к скиллу `decision`.

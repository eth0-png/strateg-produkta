"""Замер судьи «утверждение следует из цитаты». Запуск из корня: python -X utf8 docs/judge/run_judge.py [модель]
Судья видит только пару «утверждение, цитата» и не знает, какие пары искажены. Нужен Claude Code в PATH."""
import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
MODEL = sys.argv[1] if len(sys.argv) > 1 else "haiku"
CTX = "ctx" in sys.argv[2:]  # ctx: судья видит ещё и окружение цитаты в копии источника
BATCH = 30

SYSTEM = """Ты проверяешь, следует ли утверждение из дословной цитаты источника. Ты видишь только утверждение и цитату.

Ответ на каждую пару один из трёх:
- "да": всё существенное в утверждении есть в цитате. Пересказ и сокращение допустимы. Допустимы и сведения о самом источнике, которых в цитате быть не может: дата и оценка отзыва, кто автор, название источника, компании или продукта, о котором страница, оговорки вроде «в источнике не указано».
- "нет": утверждение говорит не то, что цитата. Другой период, другой охват, другое число, другой предмет, намерение или обязанность поданы как случившееся, один случай подан как массовый, смысл перевёрнут.
- "частично": основа следует из цитаты, но в утверждении есть существенная деталь о предмете, которой в цитате нет.

Не оценивай, правда ли это в мире. Оценивай только, следует ли утверждение из цитаты.
Верни только JSON-массив без пояснений вокруг: [{"n": 1, "v": "да", "why": "до 12 слов"}, ...]. Для "да" поле why пустое."""


CTX_NOTE = """

К части пар дано окружение цитаты: текст источника вокруг неё, в нижнем регистре и без кавычек. Тогда утверждение должно следовать из цитаты вместе с окружением. Деталь, которая есть в окружении, не считается добавленной."""


def judge(batch):
    text = "\n\n".join(f"{i}. Утверждение: {r['claim']}\nЦитата: «{r['quote']}»"
                       + (f"\nОкружение цитаты в источнике: «{r['context']}»" if CTX and r.get("context") else "")
                       for i, r in enumerate(batch, 1))
    system = SYSTEM + (CTX_NOTE if CTX else "")
    cmd = [shutil.which("claude"), "-p", "--model", MODEL, "--output-format", "json", "--system-prompt", system,
           "--tools", "", "--setting-sources", "project", "--strict-mcp-config"]
    t = time.time()
    p = subprocess.run(cmd, input=text, capture_output=True, text=True, encoding="utf-8", cwd=tempfile.mkdtemp())
    out = json.loads(p.stdout)
    m = re.search(r"\[.*\]", out["result"], re.S)
    verdicts = {v["n"]: v for v in json.loads(m.group(0))}
    for i, r in enumerate(batch, 1):
        v = verdicts.get(i, {})
        r["v"], r["why"] = v.get("v", "нет ответа"), v.get("why", "")
    return {"usd": out.get("total_cost_usd", 0), "sec": time.time() - t, "models": list(out.get("modelUsage", {}))}


def main():
    facts = json.loads((HERE / "facts.json").read_text(encoding="utf-8"))
    bad = json.loads((HERE / "distorted.json").read_text(encoding="utf-8"))
    ctx = {r["id"]: r.get("context", "") for r in facts}
    for r in bad:
        r["label"], r["context"] = 0, ctx.get(r["base"], "")  # искажённой паре даём окружение её исходного факта
    rows = facts + bad
    random.Random(12).shuffle(rows)
    batches = [rows[i:i + BATCH] for i in range(0, len(rows), BATCH)]
    t = time.time()
    with ThreadPoolExecutor(4) as ex:
        stats = list(ex.map(judge, batches))
    wall = time.time() - t
    (HERE / f"results-{MODEL}{'-ctx' if CTX else ''}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")

    def count(label, verdicts):
        return sum(r["label"] == label and r["v"] in verdicts for r in rows)

    nb, ng = len(bad), len(facts)
    print(f"Модель: {MODEL}{', с окружением' if CTX else ''} {sorted({m for s in stats for m in s['models']})}. Пар: {len(rows)}, пакетов: {len(batches)}.")
    print(f"Искажённые ({nb}): поймано «нет» {count(0, ['нет'])}, «частично» {count(0, ['частично'])}, пропущено «да» {count(0, ['да'])}.")
    print(f"Настоящие факты ({ng}): «да» {count(1, ['да'])}, «частично» {count(1, ['частично'])}, «нет» {count(1, ['нет'])}, "
          f"без ответа {count(1, ['нет ответа'])}.")
    print(f"Время: {wall:.0f} с по часам, {sum(s['sec'] for s in stats):.0f} с суммарно. Стоимость: ${sum(s['usd'] for s in stats):.3f}.")
    for kind in sorted({r.get("kind", "") for r in facts}):
        k = [r for r in facts if r.get("kind") == kind]
        print(f"  {kind}: {len(k)} фактов, не «да» у {sum(r['v'] != 'да' for r in k)}")


if __name__ == "__main__":
    main()

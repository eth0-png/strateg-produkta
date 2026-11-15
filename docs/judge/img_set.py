"""Замер судьи на фактах со снимков и из PDF, у которых нет текстовой копии. Запуск из корня:
  python -X utf8 docs/judge/img_set.py build            пакеты по одному на файл источника и ключ
  python -X utf8 docs/judge/img_set.py score <ответы>   сводка по файлам с ответами судьи
Пары в пакете идут под номерами P-n в случайном порядке: какие искажены, судья не знает."""
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import sa  # noqa: E402

P = ROOT / "projects" / "radar-1112"
OUT = P / "work" / "judge"
KEY = Path(__file__).parent / "results-img-key.json"


def build():
    src, cl = sa.merged(P / "sources.jsonl"), sa.merged(P / "claims.jsonl")
    rows = [{"real": c["id"], "claim": c["text"], "quote": c["quote"], "label": 1, "sid": c["src"][0]}
            for c in cl.values() if c.get("type") == "F" and c.get("status") not in sa.GONE
            and sa.quote_status(P, c, src) == "unverifiable"]
    for d in json.loads((Path(__file__).parent / "distorted-img.json").read_text(encoding="utf-8")):
        rows.append({"real": d["id"], "claim": d["claim"], "quote": d["quote"], "label": 0, "sid": cl[d["base"]]["src"][0]})
    random.Random(15).shuffle(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    key = {}
    for n, r in enumerate(rows, 1):
        r["id"] = f"P-{n}"
        key[r["id"]] = {"real": r["real"], "label": r["label"], "sid": r["sid"]}
    for sid in sorted({r["sid"] for r in rows}):
        f = OUT / f"img-{sid}.json"
        batch = [{"id": r["id"], "claim": r["claim"], "quote": r["quote"], "file": str(P / src[sid]["file"])}
                 for r in rows if r["sid"] == sid]
        f.write_text(json.dumps(batch, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{f}: пар {len(batch)}")
    KEY.write_text(json.dumps(key, ensure_ascii=False, indent=1), encoding="utf-8")


def score(files):
    key = json.loads(KEY.read_text(encoding="utf-8"))
    got = {}
    for f in files:
        for v in json.loads(re.search(r"\[.*\]", Path(f).read_text(encoding="utf-8"), re.S).group(0)):
            got[v["id"]] = v
    for label, name in ((0, "Искажённые"), (1, "Настоящие")):
        ids = [k for k, r in key.items() if r["label"] == label]
        vs = [got.get(k, {}).get("v", "нет ответа") for k in ids]
        print(f"{name} ({len(ids)}): " + ", ".join(f"«{v}» {vs.count(v)}" for v in ("да", "частично", "нет", "нет ответа")))
    print("Не «да» у настоящих и «да» у искажённых:")
    for k, r in key.items():
        v = got.get(k, {})
        if (v.get("v") == "да") != bool(r["label"]):
            print(f"  {k} = {r['real']} ({r['sid']}): «{v.get('v')}» {v.get('why', '')}")


if __name__ == "__main__":
    build() if sys.argv[1:2] == ["build"] else score(sys.argv[2:])

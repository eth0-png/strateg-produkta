"""Набор для замера судьи: все действующие факты с цитатой из трёх проектов. Запуск из корня: python docs/judge/build_set.py"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import sa  # noqa: E402



def context(P, c, src, pad):
    """Окружение цитаты в сохранённой копии: по pad знаков с каждой стороны. Текст нормализован, как при сверке цитат."""
    q = sa.norm(c["quote"])
    for sid in c.get("src", []):
        f = src.get(sid, {}).get("file")
        if f and (P / f).exists() and Path(f).suffix in sa.TEXT_EXT:
            t = sa.cached_text(str(P / f))
            i = t.find(q)
            if i >= 0:
                return t[max(0, i - pad):i + len(q) + pad]
    return ""


out = []
for pid in ("kion-trial", "salon-booking", "radar-megafon"):
    P = ROOT / "projects" / pid
    src, cl = sa.merged(P / "sources.jsonl"), sa.merged(P / "claims.jsonl")
    for c in cl.values():
        if c.get("type") == "F" and c.get("status") == "active" and c.get("quote"):
            kinds = sorted({src.get(s, {}).get("kind", "?") for s in c.get("src", [])})
            out.append({"id": f"{pid}/{c['id']}", "claim": c["text"], "quote": c["quote"], "kind": ",".join(kinds), "label": 1,
                        "source": next((src[s].get("title", "") for s in c.get("src", []) if s in src), ""),
                        "context": context(P, c, src, 700 if kinds == ["calc"] else 350)})
(Path(__file__).parent / "facts.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
by = {}
for r in out:
    by[r["kind"]] = by.get(r["kind"], 0) + 1
print(len(out), "фактов.", by, "без окружения:", sum(not r["context"] for r in out))

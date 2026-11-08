"""Объективные признаки текста стратегии: предложения с числами и их привязка к источнику.
python measure.py <файл.md> [<файл.md> ...] > out.txt"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
# то же правило «число с данными», что DATA_NUM в sa.py
NUM = re.compile(r"\d[\d\s.,]*\s?(%|процент|млн|млрд|тыс|руб|₽|\$|долл|раз\b|раза\b|чел|пользоват|подписч|отзыв)", re.I)
REF = re.compile(r"(?<![\w-])[FHPCDK]-\d+\b")
LINK = re.compile(r"https?://|\]\(")
for name in sys.argv[1:]:
    text = Path(name).read_text(encoding="utf-8")
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if len(s.strip()) > 20]
    num = [s for s in sents if NUM.search(s)]
    tied = [s for s in num if REF.search(s) or LINK.search(s)]
    urls = set(re.findall(r"https?://[^\s)\]>]+", text))
    print(f"{Path(name).name}: символов {len(text)}, предложений {len(sents)}, с числами {len(num)}, "
          f"из них с меткой или ссылкой {len(tied)}, уникальных ссылок {len(urls)}, меток F/H/P/C {len(REF.findall(text))}")

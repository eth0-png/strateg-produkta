# Кодирование отзывов App Store (ленты Мой МТС, билайн, МегаФон, по 5 страниц самых свежих).
# Показатель: доля отзывов, где текст (заголовок и тело) подпадает под тему по словарю правил.
# Числитель: число отзывов темы. Знаменатель: все прочитанные отзывы приложения (n).
# Один отзыв может попасть в несколько тем. Печатается доля «не отнесено ни к одной теме».
# Имена авторов не читаются и не печатаются.
import json, re, random, collections

FILES = {
    "МТС": ["d43731aa1b2d", "9de27ef116e9", "80b27a629245", "57023a15ada9", "e1f3354affc3"],
    "билайн": ["fe8ce09c0f75", "e63d0e5c75f8", "090e0da4ae90", "92ee3875d75b", "8a54e80f09ac"],
    "МегаФон": ["1112472988fd", "9ebedc40203e", "ad8da491f794", "838c30ad8964", "6b0759ae6f0d"],
}
THEMES = {
    "семья и близкие": r"семь|семей|близк|родител|ребён|ребен|дет[иейям]|мам[аыу]|бабушк|дедушк|муж|жена|жене",
    "общий пакет, раздача, лимит": r"общ\w+ (пакет|интернет|гигабайт|гб)|раздат|раздач|поделит|делить|лимит|делиться",
    "интернет закончился или медленный": r"закон\w+ (интернет|трафик|гб|гигабайт)|кончил|исчерп|нет интернет|без интернет|медленн|скорост|кбит|не грузит",
    "списания и деньги": r"списа|списыв|снял|снимают|деньги|денег|платёж|платеж|абонплат|двойн|баланс|тариф\w* (поднял|повысил)",
    "блокировка, отключение, неоплата": r"заблок|блокир|отключ|минус|не хватил|задолжен",
    "несколько номеров, переключение": r"два номера|двух номер|несколько номер|нескольк\w+ номер|второй номер|переключ\w+ (между )?номер|добавить номер|добавл\w+ номер|мульти|аккаунт",
    "роутер, модем, Wi-Fi": r"роутер|модем|маршрутизатор|wi-?fi|вай-?фай|вайфай|4g|usb",
    "уведомления, смс": r"уведомл|пуш|push|смс|sms",
    "поддержка и чат": r"поддержк|чат|оператор|горяч|специалист",
    "ошибки и сбои приложения": r"не открыв|вылета|ошибк|глюч|тормоз|зависа|не работает|не заходит|не могу войти|баг|сбой|не запускается",
}

def wilson(k, n, z=1.96):
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * (p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5 / (1 + z * z / n)
    return c - h, c + h

random.seed(7)
tot = collections.Counter()
for app, files in FILES.items():
    rows = []
    for f in files:
        d = json.load(open(f"materials/web/{f}.json", encoding="utf-8"))
        ent = d["feed"].get("entry", [])
        if isinstance(ent, dict):
            ent = [ent]
        for e in ent:
            if "im:rating" not in e:
                continue
            rows.append({
                "r": int(e["im:rating"]["label"]),
                "t": (e["title"]["label"] + " . " + e["content"]["label"]).lower(),
                "d": e["updated"]["label"][:10],
                "raw": e["title"]["label"] + ": " + e["content"]["label"],
            })
    n = len(rows)
    dates = sorted(x["d"] for x in rows)
    print(f"\n=== {app}: прочитано отзывов {n}, период с {dates[0]} по {dates[-1]} ===")
    dist = collections.Counter(x["r"] for x in rows)
    print("оценки:", {k: dist[k] for k in sorted(dist)})
    low = [x for x in rows if x["r"] <= 2]
    print(f"оценки 1 и 2: {len(low)} из {n}")
    for name, rx in THEMES.items():
        hit = [x for x in rows if re.search(rx, x["t"])]
        hit_low = [x for x in low if re.search(rx, x["t"])]
        lo, hi = wilson(len(hit), n)
        print(f"  {name}: {len(hit)} из {n} = {len(hit)/n:.1%} (95% от {lo:.1%} до {hi:.1%}); среди оценок 1 и 2: {len(hit_low)} из {len(low)}")
        tot[name] += len(hit)
        for x in random.sample(hit, min(3, len(hit))):
            print("     пример:", x["raw"][:220].replace("\n", " "))
    none = [x for x in rows if not any(re.search(rx, x["t"]) for rx in THEMES.values())]
    print(f"  не отнесено ни к одной теме: {len(none)} из {n} = {len(none)/n:.1%}")

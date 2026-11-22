# Расчёт к стратегии: пилот сигнала для семей (вариант 5) после короткой проверки (вариант 7), услуга (вариант 2) по условию.
# Числа брифа: S-1 (279, 285, 6 млн, 12 000 мес., 500 руб., строки таблицы). Модель вклада как в options_compare.py (S-27).
# Всё, что помечено ДОПУЩЕНИЕ, не из брифа и проверяется журналом в первом квартале и пилотом.
import math

RATE = 500
BASE, GOAL = 279.0, 285.0
GAP_MONTHS = 12000
ZA, ZB = 1.96, 0.84  # уровень 5 %, мощность 80 %

GROUPS_START, GROUPS_NOCH, GROUPS_GOAL = 6500, 8000, 12000
GROUPS_AVG = (GROUPS_START + GROUPS_NOCH) / 2
PER_GROUP = {"мало": 2.5, "средне": 3.0, "много": 3.5}  # ДОПУЩЕНИЕ: номеров в группе
SHARE_T = 0.5  # ДОПУЩЕНИЕ: половина групп получает сигнал, половина контроль (3268 групп это 50.3 % базы, S-27)
START_T, START_C = 5, 7  # ДОПУЩЕНИЕ: сигнал к 20 апреля, эффект с мая (месяц 5), контрольная часть с июля (месяц 7)
START_V2 = 10  # ДОПУЩЕНИЕ: услуга варианта 2 с октября, если пилот прошёл порог
D_V2 = 0.5  # ДОПУЩЕНИЕ: добавка услуги к эффекту сигнала, п.п. месячного оттока


def monthly_extra(numbers, d_pp, start):
    # с месяца start каждый месяц удерживается numbers*d номеров, удержанные платят до конца года
    out, kept = [], 0.0
    for m in range(1, 13):
        if m >= start:
            kept += numbers * d_pp / 100
        out.append(kept)
    return out


def plan_months(d_pp, per_group=3.0, v2=False, share_t=SHARE_T, start_t=START_T, start_c=START_C):
    n = GROUPS_AVG * per_group
    t = monthly_extra(n * share_t, d_pp, start_t)
    c = monthly_extra(n * (1 - share_t), d_pp, start_c)
    rows = [a + b for a, b in zip(t, c)]
    if v2:
        rows = [a + b for a, b in zip(rows, monthly_extra(n, D_V2, START_V2))]
    return rows


def by_quarter(rows):
    return [sum(rows[i:i + 3]) for i in (0, 3, 6, 9)]


print("== 1. Минимальный измеримый эффект пилота на отток номеров ==")
print("ДОПУЩЕНИЕ: 3 номера в группе, коэффициент кластера 1.5, наблюдение 2 месяца, базовый отток из журнала")
for share in (0.5, 0.3):
    n_t = GROUPS_START * 3 * share / 1.5
    n_c = GROUPS_START * 3 * (1 - share) / 1.5
    for p in (0.01, 0.02, 0.03):
        p2 = 1 - (1 - p) ** 2
        mde = (ZA + ZB) * math.sqrt(p2 * (1 - p2) * (1 / n_t + 1 / n_c))
        print(f"  доля с сигналом {share:.0%}, базовый отток {p:.0%} в месяц: различим эффект от {mde * 100 / 2:.2f} п.п. в месяц")

print("\n== 2. Показатель пользы: доля групп с перебоем, группы в каждой части ==")
for share in (0.5, 0.3):
    n_t, n_c = GROUPS_START * share, GROUPS_START * (1 - share)
    for p in (0.12, 0.08):
        mde = (ZA + ZB) * math.sqrt(p * (1 - p) * (1 / n_t + 1 / n_c))
        print(f"  доля с сигналом {share:.0%}, групп {n_t:.0f} против {n_c:.0f}, база {p:.0%}: различимо снижение на {mde * 100:.1f} п.п.")

print("\n== 3. Вклад за плановый год, средние допущения (3 номера в группе) ==")
for d in (0.5, 1.0, 2.0):
    for v2 in (False, True):
        rows = plan_months(d, v2=v2)
        q = by_quarter(rows)
        tot = sum(rows)
        name = "сигнал и услуга с октября" if v2 else "только сигнал"
        print(f"  d={d} п.п., {name}: по кварталам {q[0]:.0f}, {q[1]:.0f}, {q[2]:.0f}, {q[3]:.0f} мес., всего {tot:.0f} мес., {tot * RATE / 1e6:.2f} млн руб.")

print("\n== 4. Цена контрольной части: тот же сигнал на всех группах с мая ==")
for d in (0.5, 1.0):
    full = sum(plan_months(d, share_t=1.0))
    pil = sum(plan_months(d))
    print(f"  d={d} п.п.: без контроля {full * RATE / 1e6:.2f} млн, с контролем {pil * RATE / 1e6:.2f} млн, цена измерения {(full - pil) * RATE / 1e6:.2f} млн руб.")

print("\n== 5. Какое снижение оттока закрывает зазор 12 000 месяцев ==")
for v2 in (False, True):
    unit = sum(plan_months(1.0, v2=False))
    extra = sum(plan_months(0.0, v2=True)) if v2 else 0
    need = (GAP_MONTHS - extra) / unit
    name = "с услугой с октября" if v2 else "только сигнал"
    print(f"  {name}: нужно снижение оттока {need:.1f} п.п. в месяц")

print("\n== 6. Прибыль планового года и предел вложений (ДОПУЩЕНИЕ: прямые расходы c руб. на доп. месяц) ==")
for d in (0.5, 1.0, 2.0):
    tot = sum(plan_months(d))
    for c in (0, 100, 200):
        net = tot * (RATE - c) / 1e6
        print(f"  d={d} п.п., расходы {c} руб.: прибыль {BASE + net:.1f} млн руб., зазор {GOAL - BASE - net:.1f} млн, предел вложений {net:.2f} млн руб.")

print("\n== 7. Чувствительность вклада, d=1.0 п.п., расходы 100 руб. ==")
mid = sum(plan_months(1.0)) * (RATE - 100) / 1e6
print(f"  середина: {mid:.2f} млн руб.")
for k, v in PER_GROUP.items():
    print(f"  номеров в группе {v}: {sum(plan_months(1.0, per_group=v)) * (RATE - 100) / 1e6:.2f} млн руб.")
print(f"  выпуск на месяц позже (эффект с июня, контроль с августа): {sum(plan_months(1.0, start_t=6, start_c=8)) * (RATE - 100) / 1e6:.2f} млн руб.")
print(f"  выпуск на квартал позже (эффект с августа, контроль с октября): {sum(plan_months(1.0, start_t=8, start_c=10)) * (RATE - 100) / 1e6:.2f} млн руб.")
print(f"  доля с сигналом 30 %: {sum(plan_months(1.0, share_t=0.3)) * (RATE - 100) / 1e6:.2f} млн руб.")

print("\n== 8. Человеко-месяцы по ролям и кварталам (ДОПУЩЕНИЕ, подтверждает команда) ==")
PM = {
    "К1": {"аналитик": 1.5, "дизайнер": 1.0, "руководитель направления": 0.5, "разработчик (оценка)": 0.25, "юрист и безопасность": 0.25},
    "К2": {"разработчики": 2.0, "тестирование": 1.0, "аналитик": 1.5, "дизайнер": 1.0, "руководитель направления": 0.5, "поддержка": 0.25, "юрист и безопасность": 0.25},
    "К3": {"разработчики": 3.0, "тестирование": 1.0, "аналитик": 1.5, "дизайнер": 1.0, "руководитель направления": 0.5},
    "К4": {"разработчики": 1.0, "тестирование": 0.5, "аналитик": 1.5, "дизайнер": 0.5, "руководитель направления": 0.5},
}
cum_pm = []
s = 0
for q, roles in PM.items():
    s += sum(roles.values())
    cum_pm.append(s)
    print(f"  {q}: " + ", ".join(f"{r} {v}" for r, v in roles.items()) + f", всего {sum(roles.values()):.2f} чел.-мес.")
print(f"  первое полугодие (проверка и пилот): {cum_pm[1]:.2f} чел.-мес., весь год при продолжении: {cum_pm[3]:.2f} чел.-мес.")

print("\n== 9. Предельная цена человеко-месяца, при которой вложения окупаются в плановом году (расходы 100 руб.) ==")
for d in (0.5, 1.0, 2.0):
    sig = sum(plan_months(d)) * (RATE - 100) / 1e6
    full = sum(plan_months(d, v2=True)) * (RATE - 100) / 1e6
    print(f"  d={d} п.п.: только сигнал {sig:.2f} млн на {cum_pm[1]:.2f} чел.-мес. = {sig / cum_pm[1]:.3f} млн за чел.-мес., весь план {full:.2f} млн на {cum_pm[3]:.2f} чел.-мес. = {full / cum_pm[3]:.3f} млн за чел.-мес.")

print("\n== 10. Окупаемость по кварталам (ДОПУЩЕНИЕ: цена чел.-мес. 0.15 и 0.3 млн руб., расходы 100 руб.) ==")
for price in (0.15, 0.3):
    for d in (0.5, 1.0, 2.0):
        q = by_quarter(plan_months(d, v2=True))
        acc, cells = 0.0, []
        for i in range(4):
            acc += q[i] * (RATE - 100) / 1e6
            cells.append(f"К{i + 1} {acc - cum_pm[i] * price:+.2f}")
        print(f"  цена {price} млн, d={d} п.п.: накопленный итог " + ", ".join(cells) + " млн руб.")

print("\n== 11. Свод семейных групп за год (ДОПУЩЕНИЕ: выбытие групп g в месяц, повторное создание 5 %) ==")
for g in (0.01, 0.015, 0.02):
    for end in (GROUPS_NOCH, GROUPS_GOAL):
        avg = (GROUPS_START + end) / 2
        churned = avg * g * 12
        gross = end - GROUPS_START + churned
        created = gross / 0.95
        print(f"  выбытие {g:.1%}, конец года {end}: выбыло {churned:.0f}, нужно новых групп {gross:.0f}, созданий с повторами {created:.0f}")
CH = {"приглашение в приложении": 0.6, "страница тарифа и сайт": 0.25, "салон и поддержка": 0.15}  # ДОПУЩЕНИЕ
gross_noch = GROUPS_NOCH - GROUPS_START + (GROUPS_START + GROUPS_NOCH) / 2 * 0.015 * 12
print("  способы привлечения при выбытии 1.5 % и сценарии без изменений: " + ", ".join(f"{k} {gross_noch * v:.0f}" for k, v in CH.items()))

print("\n== 12. Владельцы нескольких номеров (ДОПУЩЕНИЕ: выбытие 1 % в месяц) ==")
for end in (1000, 2000):
    churned = (800 + end) / 2 * 0.01 * 12
    print(f"  конец года {end}: выбыло {churned:.0f}, нужно новых {end - 800 + churned:.0f}, это {(end - 800 + churned) / 40000:.1%} доступной базы 40000")
for d in (0.5, 1.0):
    kept = 950 * d / 100 * 3
    print(f"  сигнал о списании с октября, d={d} п.п.: удержано владельцев {kept:.0f}, доп. месяцев номеров {sum(monthly_extra(900 * 2.5, d, 10)):.0f}")

print("\n== 13. Прогноз пяти строк таблицы на конец планового года ==")
SHARE_ACT_NOCH = 5000 / 8000
for name, d, act_up, actv in (("низкий", 0.5, 0.03, 0.50), ("средний", 1.0, 0.05, 0.52), ("высокий", 2.0, 0.08, 0.55)):
    kept_groups = GROUPS_AVG * SHARE_T * d / 2 / 100 * (13 - START_T) + GROUPS_AVG * (1 - SHARE_T) * d / 2 / 100 * (13 - START_C)
    conn = GROUPS_NOCH + kept_groups
    active = conn * (SHARE_ACT_NOCH + act_up)
    profit = BASE + sum(plan_months(d)) * (RATE - 100) / 1e6
    own = 1000 + 950 * d / 100 * 3
    print(f"  {name}: прибыль {profit:.1f} млн руб., активных групп {active:.0f}, подключённых групп {conn:.0f}, владельцев {own:.0f}, активация {actv:.0%}")
print("  ДОПУЩЕНИЕ: отток групп снижается вдвое слабее оттока номеров, доля активных растёт на 3, 5, 8 п.п., активация 50, 52, 55 %")

print("\n== 14. Ориентир на конец третьего года ==")
y1 = GROUPS_NOCH + GROUPS_AVG * SHARE_T * 1.0 / 2 / 100 * 8 + GROUPS_AVG * (1 - SHARE_T) * 1.0 / 2 / 100 * 6
step = (GROUPS_GOAL - y1) / 2
y2 = y1 + step
print(f"  подключённых групп: конец года 1 {y1:.0f}, года 2 {y2:.0f}, года 3 {GROUPS_GOAL}, нужен чистый прирост {step:.0f} в год против 1500 без изменений")
print(f"  активных при 12000 подключённых и цели 8000: доля {8000 / 12000:.1%}")
avg3 = (y2 + GROUPS_GOAL) / 2
for d in (0.5, 1.0):
    months = avg3 * 3 * d / 100 * 78 * 0.95
    print(f"  третий год, d={d} п.п., контрольная часть 5 %: доп. месяцев {months:.0f}, прибыль после расходов 100 руб. {months * (RATE - 100) / 1e6:.1f} млн руб. в год")
print(f"  владельцы: с 1000 до 2000 за два года нужен чистый прирост 500 в год, это {2000 / 40000:.1%} доступной базы")

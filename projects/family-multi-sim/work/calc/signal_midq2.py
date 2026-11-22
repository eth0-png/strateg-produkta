# Проверка возражения red-team: вклад сигнала при выпуске в середине второго квартала.
# Структура как в options_compare.py: за каждый месяц эффекта удержанные номера платят до конца года.
# Показатель: накопленная валовая прибыль за плановый год, млн руб. Ставка 500 руб. за месяц номера (бриф).
# ДОПУЩЕНИЕ: 21750 номеров в семейных группах (3 номера на группу, 7250 групп), d снижение месячного оттока, п.п.
RATE = 500
N = 21750
def contrib(d_pp, months):
    saved_per_month = N * d_pp / 100
    # номера, удержанные в месяце k (k=1..months), платят ещё (months - k + 1) месяцев до конца года
    total_paid_months = sum(saved_per_month * (months - k + 1) for k in range(1, months + 1))
    return total_paid_months, total_paid_months * RATE / 1e6
for months in (9, 7.5, 7, 6):
    m = int(months)
    for d in (0.5, 1.0, 2.0):
        pm, mln = contrib(d, m)
        # половина месяца: линейная интерполяция между m и m+1
        if months != m:
            pm2, mln2 = contrib(d, m + 1)
            pm, mln = (pm + pm2) / 2, (mln + mln2) / 2
        print(f"эффект {months} мес., d={d} п.п.: {pm:.0f} доп. оплаченных месяцев, {mln:.2f} млн руб.")

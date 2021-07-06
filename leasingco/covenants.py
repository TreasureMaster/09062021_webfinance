from decimal import Decimal

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from leasingco.db import get_db

bp = Blueprint('covenants', __name__, url_prefix='/covenants')


@bp.route('/subsidiary', methods=('GET', 'POST'))
def subsidiary():
    db = get_db()
    error = None
    cursor = db.cursor()
    NAMES = {
        'equity': 1,
        'investments': 2,
        'currency': 3,
        'retained': 4
    }

    cursor.execute("SELECT * FROM SubsidiaryCovenants ORDER BY position")
    results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    print(results[3])
    cursor.execute("SELECT Year, (c1310 + c1320 + c1340 + c1350 + c1360 + c1370) AS equity, "
                   "(c1170 + c1240) AS investments, "
                   "(c1110 + c1120 + c1150 + c1160 + c1170 + c1180 + c1190 + c1210 + c1220 + c1230 + c1240 + c1250 + c1260) AS currency, "
                   "c1370 AS retained "
                   "FROM Balance "
                   "WHERE id_company=2 "
                   "ORDER BY Year")
    balance = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    print(balance)
    # каждый год
    for row in balance:
        for key, position in NAMES.items():
            results[position-1][str(row['Year'])] = row[key]
    print(results[0])
    results = {str(row['position']): row for row in results}
    print(results['1'])

    covenants = [
        {year: func(results, year, ratio).quantize(Decimal('1.00'))
        for year, ratio in zip(['2018', '2019', '2020'], ['1.18', '1.2', '1.2'])}
        for func in funcs_sub]
    covenants.insert(6, {key: 'Нарушений нет' for key in {'2018', '2019', '2020'}})
    covenants = [(lambda row, title, bank, norm: (row.update({'title': title, 'bank': bank, 'norm': norm}) or row))(row, title, bank, norm)
                 for row, title, bank, norm in zip(covenants, extras_sub['title'], extras_sub['bank'], extras_sub['norm'])]
    import pprint
    pprint.pprint(covenants)

    if results is None:
        error = 'DB is empty.'
    if error is not None:
        flash(error)
        return redirect(url_for('index'))

    return render_template('covenants/subsidiary.html', covenants=covenants)

# ---------------------------------------------------------------------------- #
funcs_sub = [
    lambda data, year, ratio=None: ((data['1'][year] - data['2'][year]
                                     - (data['7'][year]/2) - (data['10'][year])/2)
                                     / data['3'][year] * 100),
    lambda data, year, ratio=None: ((data['6'][year] / Decimal(ratio))
                                     / (data['15'][year]
                                     * (1 + ((data['16'][year] / 100)
                                     * ((1 + ((data['16'][year] / 100) / 12))
                                     ** ((data['15'][year] * 12) - 1)))))
                                     * (data['15'][year])
                                     / (data['11'][year] + data['12'][year]
                                     + data['13'][year] + data['14'][year]) * 100),
    lambda data, year, ratio=None: ((data['7'][year] + data['10'][year])
                                     / (data['1'][year] - data['2'][year]) * 100),
    lambda data, year, ratio=None: ((data['6'][year]) / (data['11'][year] + data['12'][year]
                                     + data['13'][year] + data['14'][year]) * 100),
    lambda data, year, ratio=None: ((data['11'][year] + data['12'][year])
                                     / (data['22'][year] + data['20'][year] - data['21'][year]
                                     + data['19'][year] + data['23'][year])),
    lambda data, year, ratio=None: ((data['18'][year]) / (data['17'][year]) * 100),
    lambda data, year, ratio=None: (((data['17'][year] - data['18'][year])
                                      / Decimal(ratio)) / data['11'][year]),
    lambda data, year, ratio=None: ((data['1'][year]) / (data['3'][year]) * 100),
    lambda data, year, ratio=None: ((data['5'][year]) / (data['4'][year]) * 100),
    lambda data, year, ratio=None: (data['2'][year])
]
extras_sub = {
    'title': [
        'Соотношение Собственного капитала к валюте баланса (капитализация)',
        'Соотношение Лизингового портфеля к Совокупному кредитному портфелю (Ликвидность Л1)',
        'Соотношение проблемного лизингового портфеля к Собственному капиталу (Качество активов)',
        'Соотношение суммы погашений Совокупного кредитного портфеля к сумме погашений Лизингового портфеля (Ликвидность Л2)',
        'ДОЛГ/EBITDA',
        'Доля проблемного лизингового портфеля в общей сумме портфеля (рассчитывается ежемесячно)',
        'Показатель рентабельности деятельности на уровне положительного ежеквартально',
        'Соотношение FCash/Debt',
        'Коэффицитент финансовой устойчивости',
        'Просроченная дебиторская задолженность свыше 60 (Шестидесяти) дней/Нераспределенная прибыль на уровне не более 30 (Тридцати) процентов ежеквартально',
        ('Заемщик обязан в течение срока действия Договора согласовывать '
         'с Кредитором предоставление любых заимствований третьим лицам в случае, '
         'если общая сумма предоставленных заимствований на отчетную дату, начиная с отчетности за 2 квартал 2019 г.')
    ],
    'bank': [
        'Банк 1',
        'Банк 1',
        'Банк 1',
        'Банк 1',
        'Банк 2',
        'Банк 2',
        'Банк 2',
        'Банк 2',
        'Банк 2',
        'Банк 2',
        'Банк 2'
    ],
    'norm': [
        'Более 10%',
        'Более 95%',
        'Не более 20%',
        'Не менее 120%',
        'Не более 6.5 (допускается отклонение до 7)',
        'Не более 5%',
        'Больше 0',
        'Не менее 1.5. Неустойки нет',
        'Не менее 15%',
        'Не более 30%',
        'Не более 35 000 000 руб.',
    ]
}
# ---------------------------------------------------------------------------- #


@bp.route('/parental', methods=('GET', 'POST'))
def parental():
    db = get_db()
    error = None
    cursor = db.cursor()

    cursor.execute("SELECT * FROM ParentCovenants ORDER BY position")
    results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    print(results[3])
    # Словарь по позициям
    results = {str(row['position']): row for row in results}
    print(results['1'])

    covenants = [
        {year: func(results, year)
        for year in ['2018', '2019', '2020']}
        for func in funcs]
    covenants = [(lambda row, title, bank, norm: (row.update({'title': title, 'bank': bank, 'norm': norm}) or row))(row, title, bank, norm)
                 for row, title, bank, norm in zip(covenants, extras['title'], extras['bank'], extras['norm'])]
    import pprint
    pprint.pprint(covenants)

    if results is None:
        error = 'DB is empty.'
    if error is not None:
        flash(error)
        return redirect(url_for('index'))

    return render_template('covenants/parental.html', covenants=covenants)

# ---------------------------------------------------------------------------- #
funcs = [
    lambda data, year: ((data['1'][year] + data['4'][year])
                         / (data['10'][year] - data['9'][year] + data['7'][year]
                         + data['11'][year] + data['8'][year])).quantize(Decimal('1.00')),
    lambda data, year: ('Нарушений нет'),
    lambda data, year: ('Нарушений нет'),
    lambda data, year: ('Нарушений нет' if year == '2018' else ('13 738 225.00' if year == '2019' else '46 526 146.00')),
    lambda data, year: (((data['1'][year] + data['2'][year]) / data['3'][year]) if data['3'][year] != 0 else Decimal('0.0')).quantize(Decimal('1.00'))
]
extras = {
    'title': [
        'ДОЛГ/EBITDA',
        'Показатель рентабельности деятельности на уровне положительного ежеквартально',
        ('Согласовать с Кредитором предоставление любых заимствований третьим лицам, '
         'в случае, если общая сумма предоставленных заимствований на отчетную дату, '
         'начиная с отчетности за 3 квартал 2018, превысит сумму собственного капитала'),
        ('Согласовать с Кредитором предоставление любых заимствований третьим лицам, '
         'за исключением заимствований, предоставленных компаниям ГК, если совокупная '
         'сумма таких заимствований на отчетную дату, начиная с 3 квартала 2018, превысит 50 000 000,00 рублей'),
        ('Показатель долговой нагрузки  (Финансовый долг+Гарантии)/Выручка LTM '
         '(выручка за последние 12 месяцев), начиная с 1 квартала 2020г., на уровне')
    ],
    'bank': [
        'Банк 1',
        'Банк 1',
        'Банк 1',
        'Банк 1',
        ''
    ],
    'norm': [
        'Не более 4.1 (допускается отклонение до 4.92)',
        'Не менее 0',
        '541 328',
        'Для компаний ГК нет ограничений по сумме выданных займов',
        'Не более 0,25 ежеквартально'
    ]
}
# ---------------------------------------------------------------------------- #

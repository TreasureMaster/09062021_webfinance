import datetime, copy

from dateutil.parser import parse
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from leasingco.db import get_db
from leasingco.custom_forms import PortfolioDateForm, TransferForm

from leasingco.payments import Payments

bp = Blueprint('leasing', __name__, url_prefix='/leasing')


@bp.route('/viewdate', methods=('GET', 'POST'))
def viewdate():
    db = get_db()
    error = None
    cursor = db.cursor()
    date_choice = datetime.date.today()
    form = PortfolioDateForm()
    summ = {
        'total': 0,
        'remaining': 0,
        'upto30': 0,
        '30-60': 0,
        '60-90': 0,
        'over90': 0
    }
    if request.method == 'POST':
        if request.form['action'] == 'portfolio_date':
            if form.validate_on_submit():
                date_choice = parse(request.form['portfolio_date'], dayfirst=True).date()
            else:
                error = "Неправильный ввод даты: '{}'".format(request.form['portfolio_date'])

    cursor.execute("SELECT Contract.*, CONCAT(Clients.title, ', ', Incorporation.kind) AS title, "
                   " Clients.INN as inn FROM Contract "
                   "JOIN Clients ON Contract.client_id=Clients.id "
                   "JOIN Incorporation ON Clients.incorp_id=Incorporation.id "
                   "WHERE Contract.end_date >= CONVERT(date, '{}', 23) AND Contract.begin_date <= CONVERT(date, '{}', 23) "
                   "ORDER BY Contract.number".format(date_choice, date_choice))
    portfolio = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    for row in portfolio:
        cursor.execute("SELECT payment_date FROM Payments "
                       "WHERE contract_id = {} AND "
                       "payment_date <= CONVERT(date, '{}', 23)".format(row['id'], date_choice))
        listing = [d[0] for d in cursor.fetchall()]
        lastpay_date = max(listing) if listing else None
        payment = Payments(row['total'], row['begin_date'], row['end_date'], date_choice, lastpay_date)
        row['remaining'] = payment.get_remaining()
        overdue = payment.get_overdue()
        row['debtor'] = True if (sum(overdue.values())) else False
        row['upto30'] = overdue['upto30']
        row['30-60'] = overdue['30-60']
        row['60-90'] = overdue['60-90']
        row['over90'] = overdue['over90']
        summ['upto30'] += overdue['upto30']
        summ['30-60'] += overdue['30-60']
        summ['60-90'] += overdue['60-90']
        summ['over90'] += overdue['over90']
        summ['remaining'] += row['remaining']
        summ['total'] += row['total']
    # print(portfolio[0])
    if request.method == 'POST' and request.form['table_view'] == 'должники':
        portfolio = [p for p in portfolio if p['debtor']]
        summ['total'] = sum([p['total'] for p in portfolio])
        summ['remaining'] = sum([p['remaining'] for p in portfolio])
    if portfolio is None:
        error = 'DB is empty.'
    if error is not None:
        flash(error)
        # return redirect(url_for('leasing.viewdate'))

    return render_template('reports/portfoliodate.html', portfolio_date=date_choice,
                                                         portfolio=portfolio, portfolio_form=form,
                                                         summ=summ)


@bp.route('/viewregions', methods=('GET', 'POST'))
def viewregions(date=None):
    db = get_db()
    error = None
    cursor = db.cursor()
    date_choice = datetime.date.today()
    form = PortfolioDateForm()
    summ = {
        'total': 0,
        'remaining': 0,
        'upto30': 0,
        '30-60': 0,
        '60-90': 0,
        'over90': 0,
        'portfolio_term': 0
    }
    if request.method == 'POST':
        # Выбирает текущую дату
        if request.form['action'] == 'portfolio_date':
            if form.validate_on_submit():
                date_choice = parse(request.form['portfolio_date'], dayfirst=True).date()
            else:
                error = "Неправильный ввод даты: '{}'".format(request.form['portfolio_date'])

    cursor.execute("SELECT Contract.total, CONCAT(Clients.title, ', ', Incorporation.kind) AS title, "
                   "Clients.INN as inn, Regions.region, Contract.begin_date, Contract.end_date, "
                   "Clients.id, Contract.id AS contract_id FROM Contract "
                   "JOIN Clients ON Contract.client_id=Clients.id "
                   "JOIN Regions ON Clients.region_id=Regions.id "
                   "JOIN Incorporation ON Clients.incorp_id=Incorporation.id "
                   "WHERE Contract.end_date >= CONVERT(date, '{}', 23) AND Contract.begin_date <= CONVERT(date, '{}', 23) "
                   "ORDER BY Contract.number".format(date_choice, date_choice))
    portfolio = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    # Определение даты последнего платежа для кааждого контракта
    for row in portfolio:
        cursor.execute("SELECT payment_date FROM Payments "
                       "WHERE contract_id = {} AND "
                       "payment_date <= CONVERT(date, '{}', 23)".format(row['contract_id'], date_choice))
        listing = [d[0] for d in cursor.fetchall()]
        lastpay_date = max(listing) if listing else None
        payment = Payments(row['total'], row['begin_date'], row['end_date'], date_choice, lastpay_date)
        row['remaining'] = payment.get_remaining()
        row['portfolio_term'] = (row['end_date'] - date_choice).days
        row.pop('begin_date', None)
        row.pop('end_date', None)
        summ['remaining'] += row['remaining']
        summ['total'] += row['total']
    # print(portfolio[0])
    new_portfolio = []
    # Для каждого клиента (id)
    for idx in {row['id'] for row in portfolio}:
        total = sum(row['total'] for row in portfolio if row['id']==idx)
        remaining = sum(row['remaining'] for row in portfolio if row['id']==idx)
        portfolio_term = sum(row['portfolio_term'] for row in portfolio if row['id']==idx)
        qty_term = len(list(row['portfolio_term'] for row in portfolio if row['id']==idx))
        rows = [row for row in portfolio if row['id']==idx][0]
        rows['total'] = total
        rows['remaining'] = remaining
        rows['proportion'] = remaining / summ['remaining'] * 100
        rows['portfolio_term'] = round(portfolio_term / 30 / qty_term)
        new_portfolio.append(rows)
    new_portfolio.sort(key=lambda row: row['total'], reverse=True)
    summ['proportion'] = sum(row['proportion'] for row in new_portfolio)
    summ['portfolio_term'] = round(sum(row['portfolio_term'] for row in new_portfolio) / len(new_portfolio))

    if portfolio is None:
        error = 'DB is empty.'
    if error is not None:
        flash(error)
        # return redirect(url_for('index'))
    
    return render_template('reports/portfolioregions.html', portfolio_date=date_choice,
                                                         portfolio=new_portfolio, portfolio_form=form,
                                                         summ=summ)


@bp.route('/viewtransfer', methods=('GET', 'POST'))
def viewtransfer(action=None, idx=None):
    MONTHS = [None, 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    db = get_db()
    error = None
    cursor = db.cursor()
    year_choice = datetime.date.today().year
    # print(year_choice)
    form = TransferForm()
    quarters = {}
    month_mark = True
    comms_query = ", AVG(comission) AS manager_comms "
    groupby_query = "manager"
    select_query = "manager"
    key_select = 'manager'
    if request.method == 'POST' and action is None:
        if request.form['transfer_date']:
            # if form.validate_on_submit():
            year_choice = parse(request.form['transfer_date'], dayfirst=True).date().year
            # else:
            #     error = "Неправильный ввод даты: '{}'".format(request.form['transfer_date'])
        if request.form['table_view'] == 'менеджеры':
            pass
        elif request.form['table_view'] != 'менеджеры':
            comms_query = ' '
            select_query = "DATEPART(mm, begin_date) AS month"
            groupby_query = "DATEPART(mm, begin_date)"
            key_select = 'month'
    cursor.execute("SELECT Contract.*, CONCAT(Clients.title, ', ', Incorporation.kind) AS title, "
                   "LTRIM(CONCAT(Product.prefix, ' ', Product.manufacturer, ' ', Product.model)) as tech, "
                   "Regions.region FROM Contract "
                   "JOIN Product ON Contract.product_id=Product.id "
                   "JOIN Clients ON Contract.client_id=Clients.id "
                   "JOIN Regions ON Clients.region_id=Regions.id "
                   "JOIN Incorporation ON Clients.incorp_id=Incorporation.id "
                   "WHERE DATEPART(yyyy, Contract.begin_date) = '{}' ".format(year_choice))
    contracts = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    # print(contracts[0])
    cursor.execute("SELECT {}, "
		           "COUNT(number) AS manager_contracts, "
		           "SUM(total) AS manager_total, "
		           "SUM(quantity) AS manager_qty"
		           "{}"
                   "FROM Contract "
                   "WHERE DATEPART(yyyy, begin_date) = '{}' "
                   "GROUP BY {}".format(select_query, comms_query, year_choice, groupby_query))
    managers_pred = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    # print(managers_pred)
    managers = {}
    for manager in managers_pred:
        surname = manager[key_select]
        managers[surname] = manager
        managers[surname].pop(key_select, None)
        managers[surname]['contracts'] = []
    # print(managers)
    if key_select == 'manager':
        for contract in contracts:
            managers[contract['manager']]['contracts'].append(contract)
    elif key_select != 'manager':
        for contract in contracts:
            month = contract['begin_date'].month
            managers[month]['contracts'].append(contract)
        if request.form['table_view'] == 'кварталы':
            month_mark = False
            for month in managers:
                if month in {1, 2, 3}:
                    if 'Квартал I' in quarters:
                        for entry in managers[month]:
                            if entry == 'contracts':
                                quarters['Квартал I'][entry].extend(managers[month][entry])
                            else:
                                quarters['Квартал I'][entry] += managers[month][entry]
                    else:
                        quarters['Квартал I'] = copy.deepcopy(managers[month])
                elif month in {4, 5, 6}:
                    if 'Квартал II' in quarters:
                        for entry in managers[month]:
                            if entry == 'contracts':
                                quarters['Квартал II'][entry].extend(managers[month][entry])
                            else:
                                quarters['Квартал II'][entry] += managers[month][entry]
                    else:
                        quarters['Квартал II'] = copy.deepcopy(managers[month])
                elif month in {7, 8, 9}:
                    if 'Квартал III' in quarters:
                        for entry in managers[month]:
                            if entry == 'contracts':
                                quarters['Квартал III'][entry].extend(managers[month][entry])
                            else:
                                quarters['Квартал III'][entry] += managers[month][entry]
                    else:
                        quarters['Квартал III'] = copy.deepcopy(managers[month])
                elif month in {10, 11, 12}:
                    if 'Квартал IV' in quarters:
                        for entry in managers[month]:
                            if entry == 'contracts':
                                quarters['Квартал IV'][entry].extend(managers[month][entry])
                            else:
                                quarters['Квартал IV'][entry] += managers[month][entry]
                    else:
                        quarters['Квартал IV'] = copy.deepcopy(managers[month])
    managers = quarters or managers
    managers_keys = list(managers.keys())
    managers_keys.sort()
    if contracts is None:
        error = 'DB is empty.'
    if error is not None:
        flash(error)
        # return redirect(url_for('index'))
    
    return render_template('reports/portfolio{}s.html'.format(key_select),
                            contracts=contracts, form=form, year_choice=year_choice,
                            managers=managers, managers_keys=managers_keys, months=MONTHS,
                            month_mark=month_mark)


@bp.route('/viewstorage', methods=('GET', 'POST'))
def viewstorage(action=None, idx=None):
    db = get_db()
    error = None
    storage = db.execute("SELECT Storage.*, "
                           "LTRIM(CONCAT(prefix, ' ', manufacturer, ' ', model, ' ', VIN, ' ', description)) as tech "
                           "FROM Storage "
                           "JOIN Product ON Storage.product_id=Product.id "
                           "ORDER BY receipt_date").fetchall()
    # print(storage[0])
    summ = {}
    summ['begin_qty'] = sum(row[2] for row in storage)
    summ['begin_total'] = sum(row[3] for row in storage)
    summ['end_qty'] = sum(row[2] for row in storage if row[5] is not None)
    summ['end_total'] = sum(row[3] for row in storage if row[5] is not None)
    summ['remain_qty'] = summ['begin_qty'] - summ['end_qty']
    summ['remain_total'] = summ['begin_total'] - summ['end_total']
    if storage is None:
        error = 'DB is empty.'
    if error is not None:
        flash(error)
        return redirect(url_for('index'))
    
    return render_template('reports/storage.html', storage=storage, summ=summ)


@bp.route('/viewstorbycat', methods=('GET', 'POST'))
def viewstorbycat(action=None, idx=None):
    db = get_db()
    error = None
    cursor = db.cursor()
    cursor.execute("SELECT Storage.*, ProductCategory.category, Product.manufacturer, "
                           "LTRIM(CONCAT(prefix, ' ', manufacturer, ' ', model, ' ', VIN, ' ', description)) as tech "
                           "FROM Storage "
                           "JOIN Product ON Storage.product_id=Product.id "
                           "JOIN ProductCategory ON Product.category_id=ProductCategory.id "
                           "ORDER BY receipt_date")
    storage = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    # print(storage[0])
    storage_keys = {row['category']: [] for row in storage}
    storage_results = {row['category']: {'qty': 0, 'begin': 0, 'end': 0, 'qty_end': 0, 'remain': 0, 'remain_qty': 0} for row in storage}
    # print(storage_keys)
    for row in storage:
        storage_keys[row['category']].append(row)
        storage_results[row['category']]['qty'] += row['qty']
        storage_results[row['category']]['begin'] += row['total']
        if row['expense_date'] is not None:
            storage_results[row['category']]['end'] += row['total']
            storage_results[row['category']]['qty_end'] += row['qty']
    for row in storage_results.values():
        row['remain_qty'] = row['qty'] - row['qty_end']
        row['remain'] = row['begin'] - row['end']
    summ = {
        'qty': sum(row['qty'] for row in storage_results.values()),
        'begin': sum(row['begin'] for row in storage_results.values()),
        'qty_end': sum(row['qty_end'] for row in storage_results.values()),
        'end': sum(row['end'] for row in storage_results.values()),
        'remain': sum(row['remain'] for row in storage_results.values()),
        'remain_qty': sum(row['remain_qty'] for row in storage_results.values())
    }

    if storage is None:
        error = 'DB is empty.'
    if error is not None:
        flash(error)
        return redirect(url_for('index'))
    
    return render_template('reports/storagebycategory.html', storage=storage_keys, results=storage_results, summ=summ)


@bp.route('/viewturnover', methods=('GET', 'POST'))
def viewturnover(action=None, idx=None):
    db = get_db()
    error = None
    cursor = db.cursor()
    cursor.execute("SELECT Storage.*, ProductCategory.category, Product.manufacturer, "
                           "LTRIM(CONCAT(prefix, ' ', manufacturer, ' ', model, ' ', VIN, ' ', description)) as tech "
                           "FROM Storage "
                           "JOIN Product ON Storage.product_id=Product.id "
                           "JOIN ProductCategory ON Product.category_id=ProductCategory.id "
                           "ORDER BY receipt_date")
    storage = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    # print(storage[0])
    storage_keys = {row['category']: [] for row in storage}
    storage_results = {row['category']: {'qty': 0, 'begin': 0, 'end': 0, 'qty_end': 0} for row in storage}
    # print(storage_keys)
    for row in storage:
        storage_keys[row['category']].append(row)
        storage_results[row['category']]['qty'] += row['qty']
        storage_results[row['category']]['begin'] += row['total']
        if row['expense_date'] is not None:
            storage_results[row['category']]['end'] += row['total']
            storage_results[row['category']]['qty_end'] += row['qty']
    for rows in storage_keys.values():
        for row in rows:
            if row['expense_date'] is not None:
                row['stand_days'] = (row['expense_date'] - row['receipt_date']).days
                row['remain_days'] = None
            else:
                row['stand_days'] = None
                row['remain_days'] = (datetime.date.today() - row['receipt_date']).days
    summ = {
        'qty': sum(row['qty'] for row in storage_results.values()),
        'begin': sum(row['begin'] for row in storage_results.values()),
        'qty_end': sum(row['qty_end'] for row in storage_results.values()),
        'end': sum(row['end'] for row in storage_results.values()),
    }

    if storage is None:
        error = 'DB is empty.'
    if error is not None:
        flash(error)
        return redirect(url_for('index'))
    
    return render_template('reports/turnover.html', storage=storage_keys, results=storage_results, summ=summ)
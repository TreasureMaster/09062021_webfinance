import datetime

from dateutil.parser import parse
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

# from flaskr.auth import login_required
from leasingco.db import get_db
from leasingco.models import Product, Region, Client, Incorporation, Contract
from leasingco.custom_forms import ProductForm, RegionForm, IncorpForm, ClientForm, ContractForm
from leasingco.custom_forms import PortfolioDateForm, TransferForm

from leasingco.payments import Payments

bp = Blueprint('leasing', __name__, url_prefix='/leasing')


@bp.route('/viewdate', methods=('GET', 'POST'))
def viewdate(date=None):
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
    # cursor.execute("SELECT Clients.id, CONCAT(Clients.title, ', ', Incorporation.kind) AS title FROM Clients "
    #                "JOIN Incorporation ON Clients.incorp_id=Incorporation.id")
    # form = ContractForm()
    # form.client_id.choices = [(c.id, c.title) for c in cursor.fetchall()]
    # cursor.execute("SELECT id, LTRIM(CONCAT(prefix, ' ', manufacturer, ' ', model)) as tech FROM Product")
    # form.product_id.choices = [(c.id, c.tech) for c in cursor.fetchall()]
    if request.method == 'POST':
        # print(request.form)
        if request.form['action'] == 'portfolio_date':
            date_choice = parse(request.form['portfolio_date'], dayfirst=True).date()
            print(date_choice)
            # print(type(date_choice))
            # d = (str(date_choice))
            # print(type(d))
    #     contract = Contract()
    #     contract.insert(request.form)
    # if action == 'update':
    #     contract = Contract()
    #     if request.method == 'POST':
    #         contract.update(request.form)
    #     contract.select(idx)
    #     form.client_id.default = contract.get_row()['client_id']
    #     form.product_id.default = contract.get_row()['product_id']
    #     form.process()
    #     for key, value in contract.get_row().items():
    #         if key not in {'client_id', 'product_id'}:
    #             setattr(form[key], 'data', value)
    # if action == 'delete':
    #     contract = Contract()
    #     contract.delete(idx)
    #     # redirect(url_for('product.viewproduct'))
    cursor.execute("SELECT Contract.*, CONCAT(Clients.title, ', ', Incorporation.kind) AS title, "
                   " Clients.INN as inn FROM Contract "
                   "JOIN Clients ON Contract.client_id=Clients.id "
                   "JOIN Incorporation ON Clients.incorp_id=Incorporation.id "
                   "WHERE Contract.end_date >= CONVERT(date, '{}', 23) AND Contract.begin_date <= CONVERT(date, '{}', 23) "
                   "ORDER BY Contract.number".format(date_choice, date_choice))
    # print(portfolio[0])
    # a = [dict(zip(zip(*cursor.description)[0], row)) for row in portfolio.fetchall()]
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
    print(portfolio[0])
    if request.method == 'POST' and request.form['table_view'] == 'должники':
        portfolio = [p for p in portfolio if p['debtor']]
        summ['total'] = sum([p['total'] for p in portfolio])
        summ['remaining'] = sum([p['remaining'] for p in portfolio])
    # cursor.execute("SELECT payment_date FROM Payments "
    #                "WHERE contract_id = {} AND "
    #                "payment_date <= CONVERT(date, '{}', 23)".format(portfolio[0]['id'], date_choice))
    # pays = max([d[0] for d in cursor.fetchall()])
    # print((list(cursor.fetchall())))
    # print(pays)
    # a = zip(cursor.description)
    # print(a[0])
    # port = [dict(row) for row in portfolio]
    # print(port[0])
    # # print(products[0])
    if portfolio is None:
        error = 'DB is empty.'
    if error is not None:
        flash(error)
        return redirect(url_for('index'))

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
        'over90': 0
    }
    if request.method == 'POST':
        # print(request.form)
        if request.form['action'] == 'portfolio_date':
            date_choice = parse(request.form['portfolio_date'], dayfirst=True).date()
            print(date_choice)

    cursor.execute("SELECT Contract.total, CONCAT(Clients.title, ', ', Incorporation.kind) AS title, "
                   "Clients.INN as inn, Regions.region, Contract.begin_date, Contract.end_date, "
                   "Clients.id, Contract.id AS contract_id FROM Contract "
                   "JOIN Clients ON Contract.client_id=Clients.id "
                   "JOIN Regions ON Clients.region_id=Regions.id "
                   "JOIN Incorporation ON Clients.incorp_id=Incorporation.id "
                   "WHERE Contract.end_date >= CONVERT(date, '{}', 23) AND Contract.begin_date <= CONVERT(date, '{}', 23) "
                   "ORDER BY Contract.number".format(date_choice, date_choice))
    portfolio = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    # print(portfolio[0])
    for row in portfolio:
        cursor.execute("SELECT payment_date FROM Payments "
                       "WHERE contract_id = {} AND "
                       "payment_date <= CONVERT(date, '{}', 23)".format(row['contract_id'], date_choice))
        listing = [d[0] for d in cursor.fetchall()]
        lastpay_date = max(listing) if listing else None
        payment = Payments(row['total'], row['begin_date'], row['end_date'], date_choice, lastpay_date)
        row['remaining'] = payment.get_remaining()
        row.pop('begin_date', None)
        row.pop('end_date', None)
        summ['remaining'] += row['remaining']
        summ['total'] += row['total']
    print(portfolio[0])
    new_portfolio = []
    for idx in {row['id'] for row in portfolio}:
        # print(idx)
        total = sum(row['total'] for row in portfolio if row['id']==idx)
        remaining = sum(row['remaining'] for row in portfolio if row['id']==idx)
        rows = [row for row in portfolio if row['id']==idx][0]
        rows['total'] = total
        rows['remaining'] = remaining
        rows['proportion'] = remaining / summ['remaining'] * 100
        new_portfolio.append(rows)
    new_portfolio.sort(key=lambda row: row['total'], reverse=True)
    summ['proportion'] = sum(row['proportion'] for row in new_portfolio)

    if portfolio is None:
        error = 'DB is empty.'
    if error is not None:
        flash(error)
        return redirect(url_for('index'))
    
    return render_template('reports/portfolioregions.html', portfolio_date=date_choice,
                                                         portfolio=new_portfolio, portfolio_form=form,
                                                         summ=summ)


@bp.route('/viewtransfer', methods=('GET', 'POST'))
# @bp.route('/viewtransfer/<string:action>', methods=('GET', 'POST'))
# @bp.route('/viewtransfer/<string:action>/<int:idx>', methods=('GET', 'POST'))
def viewtransfer(action=None, idx=None):
    db = get_db()
    error = None
    cursor = db.cursor()
    year_choice = datetime.date.today().year
    print(year_choice)
    form = TransferForm()
    # cursor.execute("SELECT Clients.id, CONCAT(Clients.title, ', ', Incorporation.kind) AS title FROM Clients "
    #                "JOIN Incorporation ON Clients.incorp_id=Incorporation.id")
    # form = ContractForm()
    # form.client_id.choices = [(c.id, c.title) for c in cursor.fetchall()]
    # cursor.execute("SELECT id, LTRIM(CONCAT(prefix, ' ', manufacturer, ' ', model)) as tech FROM Product")
    # form.product_id.choices = [(c.id, c.tech) for c in cursor.fetchall()]
    if request.method == 'POST' and action is None:
        print(request.form)
        year_choice = parse(request.form['transfer_date'], dayfirst=True).date().year
        comms_query = ' '
        if request.form['table_view'] == 'менеджеры':
            comms_query = ", AVG(comission) AS manager_comms "
        # contract = Contract()
        # contract.insert(request.form)
    if action == 'update':
        contract = Contract()
        # if request.method == 'POST':
        #     contract.update(request.form)
        contract.select(idx)
        # form.client_id.default = contract.get_row()['client_id']
        # form.product_id.default = contract.get_row()['product_id']
        # form.process()
        # for key, value in contract.get_row().items():
        #     if key not in {'client_id', 'product_id'}:
        #         setattr(form[key], 'data', value)
    # if action == 'delete':
    #     contract = Contract()
    #     contract.delete(idx)
    # "WHERE DATEPART(yyyy, Contract.end_date) >= '{}' AND DATEPART(yyyy, Contract.begin_date) <= '{}'"
    cursor.execute("SELECT Contract.*, CONCAT(Clients.title, ', ', Incorporation.kind) AS title, "
                   "LTRIM(CONCAT(Product.prefix, ' ', Product.manufacturer, ' ', Product.model)) as tech, "
                   "Regions.region FROM Contract "
                   "JOIN Product ON Contract.product_id=Product.id "
                   "JOIN Clients ON Contract.client_id=Clients.id "
                   "JOIN Regions ON Clients.region_id=Regions.id "
                   "JOIN Incorporation ON Clients.incorp_id=Incorporation.id "
                   "WHERE DATEPART(yyyy, Contract.begin_date) = '{}' ".format(year_choice))
    contracts = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    print(contracts[0])
    cursor.execute("SELECT manager, "
		           "COUNT(number) AS manager_contracts, "
		           "SUM(total) AS manager_total, "
		           "SUM(quantity) AS manager_qty"
		           "{}"
                   "FROM Contract "
                   "WHERE DATEPART(yyyy, begin_date) = '{}' "
                   "GROUP BY manager".format(comms_query, year_choice))
    managers_pred = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    managers = {}
    for manager in managers_pred:
        surname = manager['manager']
        managers[surname] = manager
        managers[surname].pop('manager', None)
        managers[surname]['contracts'] = []
    for contract in contracts:
        managers[contract['manager']]['contracts'].append(contract)
    managers_keys = list(managers.keys())
    managers_keys.sort()
    # print(managers_keys)
    # print(managers['Зимин'])
    if contracts is None:
        error = 'DB is empty.'
    if error is not None:
        flash(error)
        return redirect(url_for('index'))
    # if request.method == 'POST' or action == 'delete':
    #     return redirect(url_for('leasing.viewtransfer'))
    
    return render_template('reports/portfoliotransfers.html', contracts=contracts, form=form, year_choice=year_choice,
                                                              managers=managers, managers_keys=managers_keys)
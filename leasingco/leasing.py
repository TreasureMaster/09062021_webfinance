import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

# from flaskr.auth import login_required
from leasingco.db import get_db
from leasingco.models import Product, Region, Client, Incorporation, Contract
from leasingco.custom_forms import ProductForm, RegionForm, IncorpForm, ClientForm, ContractForm

from leasingco.payments import Payments

bp = Blueprint('leasing', __name__, url_prefix='/leasing')


@bp.route('/viewdate', methods=('GET', 'POST'))
@bp.route('/viewdate/<string:date>', methods=('GET', 'POST'))
def viewdate(date=None):
    db = get_db()
    error = None
    cursor = db.cursor()
    today = datetime.date.today()
    # cursor.execute("SELECT Clients.id, CONCAT(Clients.title, ', ', Incorporation.kind) AS title FROM Clients "
    #                "JOIN Incorporation ON Clients.incorp_id=Incorporation.id")
    # form = ContractForm()
    # form.client_id.choices = [(c.id, c.title) for c in cursor.fetchall()]
    # cursor.execute("SELECT id, LTRIM(CONCAT(prefix, ' ', manufacturer, ' ', model)) as tech FROM Product")
    # form.product_id.choices = [(c.id, c.tech) for c in cursor.fetchall()]
    # if request.method == 'POST' and action is None:
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
                   "ORDER BY Contract.number")
    # print(portfolio[0])
    # a = [dict(zip(zip(*cursor.description)[0], row)) for row in portfolio.fetchall()]
    portfolio = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    for row in portfolio:
        payment = Payments(row['total'], row['begin_date'], row['end_date'], today, row['lastpay_date'])
        row['remaining'] = payment.get_remaining()
    print(portfolio[0])
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
    # if request.method == 'POST' or action == 'delete':
    #     return redirect(url_for('edit.viewcontract'))
    
    return render_template('reports/portfoliodate.html', portfolio_date=today, portfolio=portfolio)

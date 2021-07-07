import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from leasingco.db import get_db
from leasingco.models import Product, Region, Client, Incorporation, Contract, PayModel, Storage
from leasingco.custom_forms import (ProductForm, RegionForm,
        IncorpForm, ClientForm, ContractForm, ChoiceContractForm, StorageForm)
from leasingco.payments import Payments

bp = Blueprint('edit', __name__, url_prefix='/edit')


@bp.route('/viewproduct', methods=('GET', 'POST'))
@bp.route('/viewproduct/<string:action>', methods=('GET', 'POST'))
@bp.route('/viewproduct/<string:action>/<int:idx>', methods=('GET', 'POST'))
def viewproduct(action=None, idx=None):
    print(request.url)
    db = get_db()
    error = None
    cursor = db.cursor()
    cursor.execute("SELECT * FROM ProductCategory")
    form = ProductForm()
    form.category_id.choices = [(g.id, g.category) for g in cursor.fetchall()]
    if request.method == 'POST' and action is None:
        product = Product()
        product.insert(request.form)
    if action == 'update':
        product = Product()
        if request.method == 'POST':
            product.update(request.form)
        product.select(idx)
        form.category_id.default = product.get_row()['category_id']
        form.process()
        for key, value in product.get_row().items():
            if key != 'category_id':
                setattr(form[key], 'data', value)
    if action == 'delete':
        product = Product()
        product.delete(idx)
    products = db.execute("SELECT Product.*, ProductCategory.category FROM Product "
                          "JOIN ProductCategory ON Product.category_id=ProductCategory.id "
                          "WHERE Product.id <> 0").fetchall()
    if products is None:
        error = 'DB is empty.'
    if error is not None:
        flash(error)
        return redirect(url_for('index'))
    if request.method == 'POST' or action == 'delete':
        return redirect(url_for('edit.viewproduct'))
    
    return render_template('edit/editproduct.html', products=products, form=form)


@bp.route('/viewregion', methods=('GET', 'POST'))
@bp.route('/viewregion/<string:action>', methods=('GET', 'POST'))
@bp.route('/viewregion/<string:action>/<int:idx>', methods=('GET', 'POST'))
def viewregion(action=None, idx=None):
    db = get_db()
    error = None
    cursor = db.cursor()
    form = RegionForm()
    if request.method == 'POST' and action is None:
        region = Region()
        region.insert(request.form)
    if action == 'update':
        # print(request.form)
        region = Region()
        
        if request.method == 'POST':
            region.update(request.form)
        region.select(idx)
        print(region.get_row())
        for key, value in region.get_row().items():
            setattr(form[key], 'data', value)
    if action == 'delete':
        region = Region()
        region.delete(idx)
    regions = cursor.execute("SELECT * FROM Regions WHERE id <> 0 ORDER BY region").fetchall()
    if regions is None:
        error = 'DB is empty.'
    if error is not None:
        flash(error)
        return redirect(url_for('index'))
    if request.method == 'POST' or action == 'delete':
        return redirect(url_for('edit.viewregion'))
    
    return render_template('edit/editregion.html', regions=regions, form=form)


@bp.route('/viewincorp', methods=('GET', 'POST'))
@bp.route('/viewincorp/<string:action>', methods=('GET', 'POST'))
@bp.route('/viewincorp/<string:action>/<int:idx>', methods=('GET', 'POST'))
def viewincorp(action=None, idx=None):
    db = get_db()
    error = None
    cursor = db.cursor()
    form = IncorpForm()
    if request.method == 'POST' and action is None:
        incorp = Incorporation()
        incorp.insert(request.form)
    if action == 'update':
        incorp = Incorporation()
        
        if request.method == 'POST':
            incorp.update(request.form)
        incorp.select(idx)
        print(incorp.get_row())
        for key, value in incorp.get_row().items():
            setattr(form[key], 'data', value)
    if action == 'delete':
        incorp = Incorporation()
        incorp.delete(idx)
    incorps = cursor.execute("SELECT * FROM Incorporation WHERE id <> 0 ORDER BY kind").fetchall()
    if incorps is None:
        error = 'DB is empty.'
    if error is not None:
        flash(error)
        return redirect(url_for('index'))
    if request.method == 'POST' or action == 'delete':
        return redirect(url_for('edit.viewincorp'))
    
    return render_template('edit/editincorp.html', incorps=incorps, form=form)


@bp.route('/viewclient', methods=('GET', 'POST'))
@bp.route('/viewclient/<string:action>', methods=('GET', 'POST'))
@bp.route('/viewclient/<string:action>/<int:idx>', methods=('GET', 'POST'))
def viewclient(action=None, idx=None):
    db = get_db()
    error = None
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Regions")
    form = ClientForm()
    form.region_id.choices = [(c.id, c.region) for c in cursor.fetchall()]
    cursor.execute("SELECT * FROM Incorporation")
    form.incorp_id.choices = [(c.id, c.kind) for c in cursor.fetchall()]
    if request.method == 'POST' and action is None:
        client = Client()
        client.insert(request.form)
    if action == 'update':
        client = Client()
        if request.method == 'POST':
            client.update(request.form)
        client.select(idx)
        form.region_id.default = client.get_row()['region_id']
        form.incorp_id.default = client.get_row()['incorp_id']
        form.process()
        for key, value in client.get_row().items():
            if key not in {'region_id', 'incorp_id'}:
                setattr(form[key], 'data', value)
    if action == 'delete':
        client = Client()
        client.delete(idx)
    clients = db.execute("SELECT Clients.*, Regions.region, Incorporation.kind FROM Clients "
                          "JOIN Regions ON Clients.region_id=Regions.id "
                          "JOIN Incorporation ON Clients.incorp_id=Incorporation.id "
                          "WHERE Clients.id <> 0").fetchall()
    if clients is None:
        error = 'DB is empty.'
    if error is not None:
        flash(error)
        return redirect(url_for('index'))
    if request.method == 'POST' or action == 'delete':
        return redirect(url_for('edit.viewclient'))
    
    return render_template('edit/editclient.html', clients=clients, form=form)


@bp.route('/viewcontract', methods=('GET', 'POST'))
@bp.route('/viewcontract/<string:action>', methods=('GET', 'POST'))
@bp.route('/viewcontract/<string:action>/<int:idx>', methods=('GET', 'POST'))
def viewcontract(action=None, idx=None):
    db = get_db()
    error = None
    cursor = db.cursor()
    cursor.execute("SELECT Clients.id, CONCAT(Clients.title, ', ', Incorporation.kind) AS title FROM Clients "
                   "JOIN Incorporation ON Clients.incorp_id=Incorporation.id")
    form = ContractForm()
    form.client_id.choices = [(c.id, c.title) for c in cursor.fetchall()]
    cursor.execute("SELECT id, LTRIM(CONCAT(prefix, ' ', manufacturer, ' ', model)) as tech FROM Product")
    form.product_id.choices = [(c.id, c.tech) for c in cursor.fetchall()]
    if request.method == 'POST' and action is None:
        contract = Contract()
        contract.insert(request.form)
    if action == 'update':
        contract = Contract()
        if request.method == 'POST':
            contract.update(request.form)
        contract.select(idx)
        form.client_id.default = contract.get_row()['client_id']
        form.product_id.default = contract.get_row()['product_id']
        form.process()
        for key, value in contract.get_row().items():
            if key not in {'client_id', 'product_id'}:
                setattr(form[key], 'data', value)
    if action == 'delete':
        contract = Contract()
        contract.delete(idx)
    contracts = db.execute("SELECT Contract.*, CONCAT(Clients.title, ', ', Incorporation.kind) AS title, "
                           "LTRIM(CONCAT(Product.prefix, ' ', Product.manufacturer, ' ', Product.model)) as tech, "
                           "Regions.region FROM Contract "
                           "JOIN Product ON Contract.product_id=Product.id "
                           "JOIN Clients ON Contract.client_id=Clients.id "
                           "JOIN Regions ON Clients.region_id=Regions.id "
                           "JOIN Incorporation ON Clients.incorp_id=Incorporation.id "
                           "ORDER BY Contract.number").fetchall()
    if contracts is None:
        error = 'DB is empty.'
    if error is not None:
        flash(error)
        return redirect(url_for('index'))
    if request.method == 'POST' or action == 'delete':
        return redirect(url_for('edit.viewcontract'))
    
    return render_template('edit/editcontract.html', contracts=contracts, form=form)


@bp.route('/viewpays', methods=('GET', 'POST'))
@bp.route('/viewpays/<string:action>', methods=('GET', 'POST'))
@bp.route('/viewpays/<string:action>/<int:idx>', methods=('GET', 'POST'))
def viewpays(action=None, idx=None):
    MONTHS = [None, 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    db = get_db()
    error = None
    cursor = db.cursor()
    cursor.execute("SELECT Contract.id, CONCAT('Договор № ', Contract.number, ' от ', Contract.begin_date, ' с ', "
                           "CONCAT(Clients.title, ', ', Incorporation.kind), ' на сумму ', Contract.total, ' руб.') "
                           "AS title FROM Contract "
                           "JOIN Clients ON Contract.client_id=Clients.id "
                           "JOIN Incorporation ON Clients.incorp_id=Incorporation.id "
                           "ORDER BY Contract.number")
    choice_form = ChoiceContractForm()
    choice_form.contract.choices = [(c.id, c.title) for c in cursor.fetchall()]
    p = {}
    years = {}
    current_contract = '0'
    marked = {}
    if request.method == 'POST' and action is None:
        current_contract = request.form['contract']
        if request.form['action'] == 'table':
            pay = PayModel()
            pay.update(request.form)
        choice_form.contract.default = current_contract
        choice_form.process()
        contract = Contract()
        contract.select(request.form['contract'])
        payments = Payments(
            contract.get_row()['total'],
            contract.get_row()['begin_date'],
            contract.get_row()['end_date'],
            contract.get_row()['begin_date'],
        ).get_payments()[1:]
        years = {d.year for d in payments}
        p = {key:{k:None for k in range(1, 13)} for key in years}
        for data in payments:
            p[data.year][data.month] = data
        pay = PayModel()
        pay.select(request.form['contract'])
        marked = pay.get_row()
    if error is not None:
        flash(error)
        return redirect(url_for('index'))
    
    return render_template('edit/editpays.html',
                            choice_form=choice_form,
                            payments=p,
                            years=years, months=MONTHS,
                            today=datetime.date.today(),
                            current_contract=current_contract,
                            marked = marked)


@bp.route('/viewstorage', methods=('GET', 'POST'))
@bp.route('/viewstorage/<string:action>', methods=('GET', 'POST'))
@bp.route('/viewstorage/<string:action>/<int:idx>', methods=('GET', 'POST'))
def viewstorage(action=None, idx=None):
    db = get_db()
    error = None
    cursor = db.cursor()
    form = StorageForm()
    cursor.execute("SELECT id, LTRIM(CONCAT(prefix, ' ', manufacturer, ' ', model, ' ', VIN, ' ', description)) as tech FROM Product")
    form.product_id.choices = [(c.id, c.tech) for c in cursor.fetchall()]
    if request.method == 'POST' and action is None:
        contract = Storage()
        contract.insert(request.form)
    if action == 'update':
        contract = Storage()
        if request.method == 'POST':
            contract.update(request.form)
        contract.select(idx)
        form.product_id.default = contract.get_row()['product_id']
        form.process()
        for key, value in contract.get_row().items():
            if key not in {'client_id', 'product_id'}:
                setattr(form[key], 'data', value)
    if action == 'delete':
        contract = Storage()
        contract.delete(idx)
    storage = db.execute("SELECT Storage.*, "
                           "LTRIM(CONCAT(prefix, ' ', manufacturer, ' ', model, ' ', VIN, ' ', description)) as tech "
                           "FROM Storage "
                           "JOIN Product ON Storage.product_id=Product.id "
                           "ORDER BY receipt_date").fetchall()
    if storage is None:
        error = 'DB is empty.'
    if error is not None:
        flash(error)
        return redirect(url_for('index'))
    if request.method == 'POST' or action == 'delete':
        return redirect(url_for('edit.viewstorage'))
    
    return render_template('edit/editstorage.html', storage=storage, form=form)
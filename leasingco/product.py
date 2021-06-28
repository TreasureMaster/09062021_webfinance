from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

# from flaskr.auth import login_required
from leasingco.db import get_db
from leasingco.models import Product, Region, Client, Incorporation, Contract
from leasingco.custom_forms import ProductForm, RegionForm, IncorpForm, ClientForm, ContractForm

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
        # print(form['model'].data)
        # form.model.data = 'model test'
        # print(form.model.data)
        # print(form['model'].data)
        form.category_id.default = product.get_row()['category_id']
        form.process()
        for key, value in product.get_row().items():
            if key != 'category_id':
                setattr(form[key], 'data', value)
    if action == 'delete':
        product = Product()
        product.delete(idx)
        # redirect(url_for('product.viewproduct'))
    products = db.execute("SELECT Product.*, ProductCategory.category FROM Product "
                          "JOIN ProductCategory ON Product.category_id=ProductCategory.id").fetchall()
    # print(products[0])
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
    # cursor.execute("SELECT * FROM ProductCategory")
    form = RegionForm()
    # form.category_id.choices = [(g.id, g.category) for g in cursor.fetchall()]
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
        # form.category_id.default = product.get_row()['category_id']
        # form.process()
        for key, value in region.get_row().items():
            # if key != 'category_id':
            setattr(form[key], 'data', value)
    if action == 'delete':
        region = Region()
        region.delete(idx)
        # redirect(url_for('product.viewproduct'))
    regions = cursor.execute("SELECT * FROM Regions ORDER BY region").fetchall()
    # print(products[0])
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
        # print(request.form)
        incorp = Incorporation()
        
        if request.method == 'POST':
            incorp.update(request.form)
        incorp.select(idx)
        print(incorp.get_row())
        # form.category_id.default = product.get_row()['category_id']
        # form.process()
        for key, value in incorp.get_row().items():
            # if key != 'category_id':
            setattr(form[key], 'data', value)
    if action == 'delete':
        incorp = Incorporation()
        incorp.delete(idx)
        # redirect(url_for('product.viewproduct'))
    incorps = cursor.execute("SELECT * FROM Incorporation ORDER BY kind").fetchall()
    # print(products[0])
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
    print(request.url)
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
        # print(form['model'].data)
        # form.model.data = 'model test'
        # print(form.model.data)
        # print(form['model'].data)
        form.region_id.default = client.get_row()['region_id']
        form.incorp_id.default = client.get_row()['incorp_id']
        form.process()
        for key, value in client.get_row().items():
            if key not in {'region_id', 'incorp_id'}:
                setattr(form[key], 'data', value)
    if action == 'delete':
        client = Client()
        client.delete(idx)
        # redirect(url_for('product.viewproduct'))
    clients = db.execute("SELECT Clients.*, Regions.region, Incorporation.kind FROM Clients "
                          "JOIN Regions ON Clients.region_id=Regions.id "
                          "JOIN Incorporation ON Clients.incorp_id=Incorporation.id").fetchall()
    # print(products[0])
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
    # print(request.url)
    db = get_db()
    error = None
    cursor = db.cursor()
    cursor.execute("SELECT Clients.id, CONCAT(Clients.title, ',', Incorporation.kind) AS title FROM Clients "
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
        # redirect(url_for('product.viewproduct'))
    contracts = db.execute("SELECT Contract.*, CONCAT(Clients.title, ', ', Incorporation.kind) AS title, "
                           "LTRIM(CONCAT(Product.prefix, ' ', Product.manufacturer, ' ', Product.model)) as tech, "
                           "Regions.region FROM Contract "
                           "JOIN Product ON Contract.product_id=Product.id "
                           "JOIN Clients ON Contract.client_id=Clients.id "
                           "JOIN Regions ON Clients.region_id=Regions.id "
                           "JOIN Incorporation ON Clients.incorp_id=Incorporation.id").fetchall()
    # print(products[0])
    if contracts is None:
        error = 'DB is empty.'
    if error is not None:
        flash(error)
        return redirect(url_for('index'))
    if request.method == 'POST' or action == 'delete':
        return redirect(url_for('edit.viewcontract'))
    
    return render_template('edit/editcontract.html', contracts=contracts, form=form)

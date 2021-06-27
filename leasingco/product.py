from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

# from flaskr.auth import login_required
from leasingco.db import get_db
from leasingco.models import Product, Region
from leasingco.custom_forms import ProductForm, RegionForm

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

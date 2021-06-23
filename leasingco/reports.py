from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

# from flaskr.auth import login_required
from leasingco.db import get_db

bp = Blueprint('reports', __name__)


@bp.route('/')
def index():
    g.user = True
    # db = get_db()
    # posts = db.execute(
    #     'SELECT p.id, title, body, created, author_id, username'
    #     ' FROM post p JOIN user u ON p.author_id = u.id'
    #     ' ORDER BY created DESC'
    # ).fetchall()
    return render_template('index.html')

@bp.route('/parent')
def parent():
    db = get_db()
    cursor = db.cursor()
    select = "SELECT * FROM Balance WHERE id_company=1"
    cursor.execute(select)
    # years = cursor.fetchall()
    years = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    print(years[0])
    select_titles = "SELECT code, title FROM ReportsTitle WHERE code < 2000"
    cursor.execute(select_titles)
    balance_titles = cursor.fetchall()
    # print(balance_titles)
    # print(type(balance_titles))
    balance_titles = [{'title': title, 'code': code} for code, title in balance_titles]
    balance = []
    for year in years:
        # print(year['Year'])
        for row in balance_titles:
            idx = 'c' + str(row['code'])
            # print(idx)
            # balance.append(dict(**row, **{'year': 2020}))
            balance.append(dict(**row,
                **({str(year['Year']): year[idx]} if idx in year else {str(year['Year']): None})
            ))
            # balance.append(row)
    print(balance[5])
    # print(balance_titles)
    # for year in years:
    #     print(year[3])
    # if request.method == 'POST':
    #     title = request.form['title']
    #     body = request.form['body']
    #     error = None

    #     if not title:
    #         error = 'Title is required.'

    #     if error is not None:
    #         flash(error)
    #     else:
    #         db = get_db()
    #         db.execute(
    #             'INSERT INTO post (title, body, author_id)'
    #             ' VALUES (?, ?, ?)',
    #             (title, body, g.user['id'])
    #         )
    #         db.commit()
    #         return redirect(url_for('blog.index'))

    return render_template('reports/report.html', years=years)
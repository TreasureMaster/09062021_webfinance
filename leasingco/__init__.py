import os

from flask import Flask
from flask_bs4 import Bootstrap


def create_app(test_config=None):
    # создать и настроить приложение
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DBSERVER_NAME='DESKTOP-4T6BA5S',
        DATABASE_NAME='GroupCompanies'
        # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # загрузить конфигурацию экземпляра, если он существует, когда не тестируем
        app.config.from_pyfile('config.py', silent=True)
    else:
        # загрузить тестовую конфигурацию, если она передана
        app.config.from_mapping(test_config)

    # убедитесь, что папка экземпляра существует
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Подключаем Бутстрап
    Bootstrap(app)
    app.config['BOOTSTRAP_CDN_FORCE_SSL'] = True

    from . import db
    db.init_app(app)

    from . import reports
    app.register_blueprint(reports.bp)
    app.add_url_rule('/', endpoint='index')

    # простая страница, которая здоровается
    @app.route('/hello')
    def hello():
        print(app.config)
        return 'Hello, World!'

    # Фильтр числа
    @app.template_filter('pdigit')
    def pretty_digit(digit):
        text = ''
        digit = str(digit)
        if '.' in digit:
            first, second = digit.split('.')
            second = '.' + second
        else:
            first = digit
            second = ''
        if first.startswith('-'):
            first = first[1:]
            sign = '-'
        else:
            sign = ''
        for num, char in enumerate(reversed(first), start=0):
            if num % 3:
                text = char + text
            else:
                text = char + ' ' + text
        text = sign + text.strip() + second
        return text

    # Коррекция 0.5 вверх
    @app.template_filter('half')
    def pretty_half(digit):
        from decimal import Decimal
        f = int(digit)
        if (digit - f) == 0.5:
            return digit + Decimal('0.01')
        elif (digit - f) == -0.5:
            return digit - Decimal('0.01')
        return digit

    return app

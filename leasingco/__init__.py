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

    return app
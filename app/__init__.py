# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# import os
#
# db = SQLAlchemy()
# migrate = Migrate()
#
# def create_app():
#     app = Flask(__name__)
#     app.config.from_object('app.config.Config')
#
#     db.init_app(app)
#     migrate.init_app(app, db)
#
#     from app.routes import main as main_blueprint
#     app.register_blueprint(main_blueprint)
#
#     return app
import pymysql

pymysql.install_as_MySQLdb()
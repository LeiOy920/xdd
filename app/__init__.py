from flask import Flask
from flask_cors import CORS




def create_app():
    from app.config import app

    CORS(app)

    from app.routes.movieDetails.dm import dm
    from app.routes.BigScreen.bangdan import bd
    from app.routes.BigScreen.mapChart import mp

    app.register_blueprint(dm, url_prefix='/dm')
    app.register_blueprint(mp, url_prefix='/map')
    app.register_blueprint(bd, url_prefix='/bd')

    return app

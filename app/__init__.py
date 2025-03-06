from flask import Flask
from flask_cors import CORS

from app.routes.movieDetails.detail import detail


def create_app():
    from app.config import app

    CORS(app)

    from app.routes.movieDetails.dm import dm
    from app.routes.BigScreen.bangdan import bd
    from app.routes.BigScreen.mapChart import mp
<<<<<<< HEAD
    from app.routes.realtime.main_panel import mainpanel
=======
    from app.routes.es.search import ess
>>>>>>> 32eab978673d6f07a27b8eb44fc5d63387b1f32c

    app.register_blueprint(dm, url_prefix='/dm')
    app.register_blueprint(mp, url_prefix='/map')
    app.register_blueprint(bd, url_prefix='/bd')
<<<<<<< HEAD
    app.register_blueprint(mainpanel, url_prefix='/mainpanel')
=======
    app.register_blueprint(ess, url_prefix='/es')
    app.register_blueprint(detail, url_prefix='/detail')
>>>>>>> 32eab978673d6f07a27b8eb44fc5d63387b1f32c

    return app

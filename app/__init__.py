from flask import Flask
from flask_cors import CORS


def create_app():
    from app.config import app

    CORS(app)

    from app.routes.movieDetails.dm import dm
    from app.routes.BigScreen.bangdan import bd
    from app.routes.BigScreen.mapChart import mp
    from app.routes.realtime.main_panel import mainpanel
    from app.routes.realtime.right_info import rightinfo
    from app.routes.es.search import ess
    from app.routes.BigScreen.BoxOfficeTrend import trend
    from app.routes.BigScreen.personnel import personnel
    from app.routes.movieDetails.detail import detail
    from app.routes.movieDetails.movie_recommend import mr_blueprint

    app.register_blueprint(dm, url_prefix='/dm')
    app.register_blueprint(mp, url_prefix='/map')
    app.register_blueprint(bd, url_prefix='/bd')
    app.register_blueprint(mainpanel, url_prefix='/mainpanel')
    app.register_blueprint(rightinfo, url_prefix='/rightinfo')
    app.register_blueprint(ess, url_prefix='/es')
    app.register_blueprint(detail, url_prefix='/detail')
    app.register_blueprint(trend, url_prefix='/trend')
    app.register_blueprint(personnel, url_prefix='/personnel')
    app.register_blueprint(mr_blueprint, url_prefix='/mr')

    return app

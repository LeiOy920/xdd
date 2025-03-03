from app.config import db


class MapData (db.Model):
    __tablename__ = "map_data"
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    region = db.Column(db.String(255))
    m_rank = db.Column(db.Integer)
    movie_name = db.Column(db.String(255))
    rating = db.Column(db.DECIMAL)

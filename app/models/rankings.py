from app.config import db


class Rankings (db.Model):
    __tablename__ = "rankings"
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    ranking_type = db.Column(db.String(255))
    r_rank = db.Column(db.Integer)
    movie_name = db.Column(db.String(255))
    quantity = db.Column(db.String(255))
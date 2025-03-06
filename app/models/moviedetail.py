from app.config import db


class MovieDetail(db.Model):
    __tablename__ = "moviedetail"
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    movie_image = db.Column(db.Text)
    movie_name = db.Column(db.String(255))
    screenwriter = db.Column(db.Text)
    starring = db.Column(db.Text)
    director = db.Column(db.String(255))
    genre = db.Column(db.String(255))
    language = db.Column(db.String(255))
    release_date = db.Column(db.DateTime)
    runtime = db.Column(db.Integer)
    also_known_as = db.Column(db.Text)
    douban_rating = db.Column(db.Float)
    production_country_region = db.Column(db.String(255))
    review_file_path = db.Column(db.Text)


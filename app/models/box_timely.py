from app.config import db


class BoxTimely (db.Model):
    __tablename__ = "box_timely"
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    m_id = db.Column(db.Integer)
    movie_name = db.Column(db.String(255))
    today_box = db.Column(db.String(255))
    proportion = db.Column(db.String(255))
    slots_num = db.Column(db.Integer)
    slots_proportion = db.Column(db.String(255))
    average_person = db.Column(db.DECIMAL)
    occupancy_rate = db.Column(db.String(255))
    day1_box = db.Column(db.String(255))
    day2_box = db.Column(db.String(255))
    day3_box = db.Column(db.String(255))
    day4_box = db.Column(db.String(255))
    release_days = db.Column(db.Integer)
    total_box = db.Column(db.String(255))

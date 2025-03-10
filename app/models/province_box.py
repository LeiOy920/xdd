from app.config import db


class ProvinceBox (db.Model):
    __tablename__ = "province_box"
    p_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    province = db.Column(db.String(255))
    box_count = db.Column(db.DECIMAL)

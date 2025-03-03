from app.config import db


class BoxOfficeTrend (db.Model):
    __tablename__ = "box_office_trend"
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    m_id = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    quantity = db.Column(db.DECIMAL)

from app.config import db


class SentimentScore (db.Model):
    __tablename__ = "sentiment_score"
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    m_id = db.Column(db.Integer)
    very_like = db.Column(db.Integer)
    s_like = db.Column(db.Integer)
    normal = db.Column(db.Integer)
    dislike = db.Column(db.Integer)
    very_dislike = db.Column(db.Integer)
    total_references = db.Column(db.Integer)
    average_score = db.Column(db.DECIMAL)
from app.config import db


class DieGraphData (db.Model):
    __tablename__ = "die_graph_data"
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    data_name = db.Column(db.String(255))
    chart_type = db.Column(db.String(255))
    data_file_path = db.Column(db.Text)


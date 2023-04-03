from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Data(db.Model):
    __tablename__ = 'data'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    emg_1 = db.Column(db.Float)
    emg_2 = db.Column(db.Float)
    emg_3 = db.Column(db.Float)
    acc = db.Column(db.Float)
    time_recorded = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f"<Data(email='{self.email}', data='{self.data}', time_recorded='{self.time_recorded}')>"

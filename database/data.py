from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Data(db.Model):
    __tablename__ = 'data'

    id = Column

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    data = Column(ARRAY(Integer, dimensions=1))
    time_recorded = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Data(email='{self.email}', data='{self.data}', time_recorded='{self.time_recorded}')>"

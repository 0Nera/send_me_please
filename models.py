from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class HashRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hash_value = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
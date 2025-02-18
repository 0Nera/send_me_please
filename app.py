from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db, HashRecord
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///virus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per day", "20 per hour"]
)

@app.route('/')
def index():
    total_hashes = HashRecord.query.count()
    weekly_hashes = HashRecord.query.filter(HashRecord.timestamp >= datetime.now() - timedelta(days=7)).count()

    weekly_hashes_data = []
    for i in range(7):
        day = datetime.now() - timedelta(days=i)
        count = HashRecord.query.filter(
            db.func.date(HashRecord.timestamp) == day.date()
        ).count()
        weekly_hashes_data.insert(0, count)

    return render_template('index.html', 
                           total_hashes=total_hashes, 
                           weekly_hashes=weekly_hashes, 
                           weekly_hashes_data=weekly_hashes_data)

@app.route('/upload', methods=['POST'])
@limiter.limit("10/minute")
def upload_hash():
    data = request.json
    hash_value = data.get('hash')

    if not hash_value:
        return jsonify({"error": "No hash provided"}), 400

    new_record = HashRecord(hash_value=hash_value)
    db.session.add(new_record)
    db.session.commit()

    return jsonify({"message": "Hash received"}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
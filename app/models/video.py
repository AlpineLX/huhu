from app.models import db
from datetime import datetime
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(128), unique=True, nullable=False)
    user_id = db.Column(db.String(80), unique=False, nullable=False)
    video_path = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_size = db.Column(db.Float, nullable=True)  # Store in MB
    duration = db.Column(db.Integer, nullable=True)  # Store in seconds
    processed_video_path = db.Column(db.String(255))
    status = db.Column(db.String(50), default='pending')

    # New fields for pixel coordinate positions
    xini = db.Column(db.Integer, nullable=True)
    yini = db.Column(db.Integer, nullable=True)
    xend = db.Column(db.Integer, nullable=True)
    yend = db.Column(db.Integer, nullable=True)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

db = SQLAlchemy()

# ---------------- USER ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)  # Changed from 10 to 20 for international numbers
    password_hash = db.Column(db.String(128), nullable=False)
    gender = db.Column(db.String(10))
    age = db.Column(db.String(10))
    
    # NEW FIELDS FOR AVATAR
    avatar_color = db.Column(db.String(100), default='linear-gradient(135deg, #FFD166, #FFCC00)')
    avatar_icon = db.Column(db.String(50), default='fa-user')
    
    # NEW FIELDS FOR STATISTICS
    drawings_created = db.Column(db.Integer, default=0)
    favorites_count = db.Column(db.Integer, default=0)
    days_active = db.Column(db.Integer, default=1)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Method to update last active
    def update_last_active(self):
        self.last_active = datetime.utcnow()
        db.session.commit()
    
    # Method to increment drawings count
    def increment_drawings(self):
        self.drawings_created += 1
        db.session.commit()
    
    # Method to update days active
    def update_days_active(self):
        today = datetime.utcnow().date()
        last_active_date = self.last_active.date()
        
        if today > last_active_date:
            self.days_active += 1
            self.last_active = datetime.utcnow()
            db.session.commit()
    
    # Consolidated methods to avoid duplicates
    def update_last_active_consolidated(self):
        self.last_active = datetime.utcnow()
        db.session.commit()
    
    def increment_drawings_consolidated(self):
        self.drawings_created += 1
        db.session.commit()
    
    def update_days_active_consolidated(self):
        """Update days active counter"""
        from datetime import datetime
        today = datetime.utcnow().date()
        
        # Check if last_active exists
        if not hasattr(self, 'last_active') or self.last_active is None:
            self.last_active = datetime.utcnow()
            self.days_active = 1
        else:
            last_active_date = self.last_active.date()
            
            if today > last_active_date:
                self.days_active += 1
                self.last_active = datetime.utcnow()
        
        db.session.commit()


# ---------------- QUIZ RESULT ----------------
class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date_taken = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------- COINS ----------------
class Coins(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    coins = db.Column(db.Integer, default=0)


# ---------------- SHAPE BUILDER RESULT ----------------
class ShapeResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    similarity_score = db.Column(db.Integer, nullable=False)
    coins_awarded = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------- MATH GAME RESULT ----------------
class MathResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    level_completed = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    coins_awarded = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

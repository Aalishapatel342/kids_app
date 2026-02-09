from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import random
import json

db = SQLAlchemy()

# ---------------- USER ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    gender = db.Column(db.String(10))
    age = db.Column(db.String(10))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Relationship to ColorSpin
    color_spins = db.relationship('ColorSpin', backref='user', lazy=True)


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


# ---------------- COLOR CARNIVAL MODELS ----------------

class ColorSpin(db.Model):
    """Stores each spin result from Color Carnival Wheel"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    spin_result = db.Column(db.String(50), nullable=False)  # Color name
    color_hex = db.Column(db.String(7), nullable=False)     # Hex code
    coins_earned = db.Column(db.Integer, default=0)
    spin_data = db.Column(db.Text)  # JSON data of the spin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ColorWheelStats(db.Model):
    """Aggregated statistics for Color Carnival"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_spins = db.Column(db.Integer, default=0)
    favorite_color = db.Column(db.String(50))
    total_coins_earned = db.Column(db.Integer, default=0)
    last_spin_date = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ---------------- COLOR CARNIVAL LOGIC CLASSES ----------------

class ColorWheelLogic:
    """Business logic for Color Carnival Wheel"""
    
    # Colors from your reference image (12 segments)
    COLORS = [
        {"name": "Red", "hex": "#FF5252", "value": 5},
        {"name": "Deep Orange", "hex": "#FF8A65", "value": 4},
        {"name": "Orange", "hex": "#FFCC80", "value": 3},
        {"name": "Pink", "hex": "#FF80AB", "value": 5},
        {"name": "Purple", "hex": "#B388FF", "value": 7},
        {"name": "Indigo", "hex": "#536DFE", "value": 6},
        {"name": "Blue", "hex": "#448AFF", "value": 4},
        {"name": "Light Blue", "hex": "#80D8FF", "value": 3},
        {"name": "Light Green", "hex": "#69F0AE", "value": 5},
        {"name": "Yellow", "hex": "#FFFF8D", "value": 2},
        {"name": "Yellow Green", "hex": "#CCFF90", "value": 4},
        {"name": "Green Cyan", "hex": "#A7FFEB", "value": 6}
    ]
    
    @classmethod
    def get_wheel_data(cls):
        """Get wheel configuration for frontend"""
        return {
            "colors": cls.COLORS,
            "segments": len(cls.COLORS),
            "segment_angle": 360 / len(cls.COLORS)
        }
    
    @classmethod
    def spin_wheel(cls):
        """Simulate a spin and return result"""
        # Randomly select a color
        selected = random.choice(cls.COLORS)
        
        # Add spin animation data
        spin_data = {
            "selected_color": selected,
            "spin_angle": random.randint(0, 359),
            "rotations": random.randint(3, 6),
            "duration": random.uniform(2.5, 4.0),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return spin_data
    
    @classmethod
    def calculate_coins(cls, color_name):
        """Calculate coins earned for a color"""
        for color in cls.COLORS:
            if color["name"] == color_name:
                return color["value"]
        return 0


class ColorCarnivalManager:
    """Manager class for Color Carnival operations"""
    
    @staticmethod
    def record_spin(user_id, spin_result, color_hex, spin_data):
        """Record a spin in database"""
        from app import db
        
        # Calculate coins earned
        coins_earned = ColorWheelLogic.calculate_coins(spin_result)
        
        # Create spin record
        spin = ColorSpin(
            user_id=user_id,
            spin_result=spin_result,
            color_hex=color_hex,
            coins_earned=coins_earned,
            spin_data=json.dumps(spin_data)
        )
        
        # Update user's coins
        coins_obj = Coins.query.filter_by(user_id=user_id).first()
        if not coins_obj:
            coins_obj = Coins(user_id=user_id, coins=0)
            db.session.add(coins_obj)
        
        coins_obj.coins += coins_earned
        
        # Update or create stats
        stats = ColorWheelStats.query.filter_by(user_id=user_id).first()
        if not stats:
            stats = ColorWheelStats(user_id=user_id)
            db.session.add(stats)
        
        stats.total_spins += 1
        stats.total_coins_earned += coins_earned
        stats.last_spin_date = datetime.utcnow()
        
        # Update favorite color
        ColorCarnivalManager._update_favorite_color(user_id, spin_result)
        
        db.session.add(spin)
        db.session.commit()
        
        return {
            "spin_id": spin.id,
            "coins_earned": coins_earned,
            "total_coins": coins_obj.coins
        }
    
    @staticmethod
    def _update_favorite_color(user_id, color_name):
        """Update user's favorite color based on spin history"""
        from app import db
        
        stats = ColorWheelStats.query.filter_by(user_id=user_id).first()
        if not stats:
            return
        
        # Count color occurrences
        spins = ColorSpin.query.filter_by(user_id=user_id).all()
        color_counts = {}
        
        for spin in spins:
            color_counts[spin.spin_result] = color_counts.get(spin.spin_result, 0) + 1
        
        # Find most frequent color
        if color_counts:
            favorite = max(color_counts, key=color_counts.get)
            stats.favorite_color = favorite
    
    @staticmethod
    def get_user_stats(user_id):
        """Get user's Color Carnival statistics"""
        stats = ColorWheelStats.query.filter_by(user_id=user_id).first()
        
        if not stats:
            return {
                "total_spins": 0,
                "total_coins_earned": 0,
                "favorite_color": None,
                "last_spin": None,
                "spin_history": []
            }
        
        # Get recent spins
        recent_spins = ColorSpin.query.filter_by(user_id=user_id)\
            .order_by(ColorSpin.created_at.desc())\
            .limit(10)\
            .all()
        
        spin_history = [
            {
                "id": spin.id,
                "color": spin.spin_result,
                "hex": spin.color_hex,
                "coins": spin.coins_earned,
                "time": spin.created_at.strftime("%H:%M %p")
            }
            for spin in recent_spins
        ]
        
        return {
            "total_spins": stats.total_spins,
            "total_coins_earned": stats.total_coins_earned,
            "favorite_color": stats.favorite_color,
            "last_spin": stats.last_spin_date.strftime("%Y-%m-%d %H:%M") if stats.last_spin_date else None,
            "spin_history": spin_history
        }
    
    @staticmethod
    def get_leaderboard(limit=10):
        """Get Color Carnival leaderboard"""
        from app import db
        from sqlalchemy import func
        
        # Get top users by total coins earned from Color Carnival
        leaderboard = db.session.query(
            User.username,
            func.sum(ColorSpin.coins_earned).label('total_coins'),
            func.count(ColorSpin.id).label('total_spins')
        ).join(
            ColorSpin, User.id == ColorSpin.user_id
        ).group_by(
            User.id
        ).order_by(
            func.sum(ColorSpin.coins_earned).desc()
        ).limit(limit).all()
        
        return [
            {
                "rank": i + 1,
                "username": item[0],
                "total_coins": int(item[1]) if item[1] else 0,
                "total_spins": item[2]
            }
            for i, item in enumerate(leaderboard)
        ]
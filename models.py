from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
import uuid

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    auth_provider = db.Column(db.String(20), default='local')  # local, google
    auth_provider_id = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    last_active = db.Column(db.DateTime, server_default=db.func.now())

    horse_profile = db.relationship('HorseProfile', uselist=False, backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.public_id,
            'email': self.email,
            'username': self.username,
            'auth_provider': self.auth_provider,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class HorseProfile(db.Model):
    __tablename__ = 'horse_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    # Basic
    display_name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    photo_url = db.Column(db.String(500))
    age = db.Column(db.Integer)
    breed = db.Column(db.String(100))
    gender = db.Column(db.String(20))  # mare, stallion, gelding
    height_hands = db.Column(db.Float)  # height in hands

    # Horse-specific personality/preferences
    experience_level = db.Column(db.String(30))  # beginner, intermediate, advanced, expert
    riding_discipline = db.Column(db.String(100))  # dressage, jumping, western, trail, etc.
    temperament = db.Column(db.String(50))  # calm, spirited, eager, gentle, etc.
    ideal_date_activity = db.Column(db.String(200))  # pasture grazing, trail ride, arena work
    stable_region = db.Column(db.String(100))
    favorite_treat = db.Column(db.String(100))
    wants_offspring = db.Column(db.Boolean, default=False)
    coat_color = db.Column(db.String(50))
    markings = db.Column(db.Text)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'display_name': self.display_name,
            'bio': self.bio,
            'photo_url': self.photo_url,
            'age': self.age,
            'breed': self.breed,
            'gender': self.gender,
            'height_hands': self.height_hands,
            'experience_level': self.experience_level,
            'riding_discipline': self.riding_discipline,
            'temperament': self.temperament,
            'ideal_date_activity': self.ideal_date_activity,
            'stable_region': self.stable_region,
            'favorite_treat': self.favorite_treat,
            'wants_offspring': self.wants_offspring,
            'coat_color': self.coat_color,
            'markings': self.markings,
        }


class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending')  # pending, matched, rejected
    matched_at = db.Column(db.DateTime)
    conversation_prompt = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user1 = db.relationship('User', foreign_keys=[user1_id])
    user2 = db.relationship('User', foreign_keys=[user2_id])

    __table_args__ = (
        db.UniqueConstraint('user1_id', 'user2_id', name='unique_match'),
    )

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# Create database object
db = SQLAlchemy()

# Student table
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer)
    branch = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    status = db.Column(db.String(50), default="Applied")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "age": self.age,
            "branch": self.branch,
            "phone": self.phone,
            "status": self.status,
            "is_active": self.is_active,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None
        }




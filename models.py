from flask_sqlalchemy import SQLAlchemy

# Create database object
db = SQLAlchemy()

# Student table
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer)
    branch = db.Column(db.String(100))

    status = db.Column(db.String(50), default="Applied")
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "age": self.age,
            "branch": self.branch,
            "status": self.status,
            "is_active": self.is_active
        }




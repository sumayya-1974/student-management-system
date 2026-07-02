import os
import csv
import io
from flask import Response
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, Student, Admin
from dotenv import load_dotenv
from flasgger import Swagger
load_dotenv()

app = Flask(__name__)
Swagger(app)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "database.db"))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Login required"}), 401

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@app.route("/")
def home():
    return "Student Management System API is running."

@app.route("/login", methods=["POST"])
def login():
    """
    Admin Login
    ---
    tags:
      - Authentication
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      401:
        description: Invalid username or password
    """
    data = request.get_json()
    

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    username = data.get("username")
    password = data.get("password")

    admin = Admin.query.filter_by(username=username).first()

    if admin and bcrypt.check_password_hash(admin.password, password):
        login_user(admin)
        return jsonify({
            "message": "Login successful",
            "admin": {
                "id": admin.id,
                "username": admin.username
            }
        })

    return jsonify({"error": "Invalid username or password"}), 401

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"})

@app.route("/me", methods=["GET"])
@login_required
def me():
    """
    Get current logged-in admin
    ---
    tags:
      - Authentication
    responses:
      200:
        description: Returns the logged-in admin details
      401:
        description: Login required
    """ 
    return jsonify({
        "id": current_user.id,
        "username": current_user.username
    })

@app.route("/add_student", methods=["POST"])
@login_required
def add_student():
    """
    Add a new student
    ---
    tags:
      - Students
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
          properties:
            name:
              type: string
              example: Rahul Sharma
            email:
              type: string
              example: rahul@example.com
            age:
              type: integer
              example: 21
            branch:
              type: string
              example: Biotechnology
            phone:
              type: string
              example: "9876543210"
            status:
              type: string
              example: Applied
    responses:
      200:
        description: Student added successfully
      400:
        description: Invalid input or email already exists
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON received"}), 400
    
    if not data.get("name") or not data.get("email"):
        return jsonify({"error": "Name and email are required"}), 400

    existing_student = Student.query.filter_by(email=data["email"]).first()
    if existing_student:
        return jsonify({"error": "Email already exists"}), 400

    student = Student(
        name=data["name"],
        email=data["email"],
        age=data.get("age"),
        branch=data.get("branch"),
        phone=data.get("phone"),
        status=data.get("status", "Applied")
    )

    db.session.add(student)
    db.session.commit()

    return jsonify({
        "message": "Student added successfully",
        "student": student.to_dict()
    })

@app.route("/students", methods=["GET"])
@login_required
def view_students():
    """
    View all active students
    ---
    tags:
      - Students
    responses:
      200:
        description: List of all active students
    """
    students = Student.query.filter_by(is_active=True).all()
    return jsonify([s.to_dict() for s in students])

#  DELETE ROUTE 

@app.route("/delete_student/<int:student_id>", methods=["DELETE"])
@login_required
def delete_student(student_id):
    """
    Soft delete a student
    ---
    tags:
      - Students
    parameters:
      - in: path
        name: student_id
        required: true
        type: integer
        description: ID of the student to delete
    responses:
      200:
        description: Student soft-deleted successfully
      400:
        description: Active student cannot be deleted
      404:
        description: Student not found
    """
    student = Student.query.get(student_id)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    if student.status == "Active":
        return jsonify({
            "error": "Active student cannot be deleted. Change status first."
        }), 400

    # Soft delete
    student.is_active = False
    db.session.commit()

    return jsonify({"message": "Student soft-deleted successfully"})

#update route
@app.route("/update_student/<int:student_id>", methods=["PUT"])
@login_required
def update_student(student_id):
    """
    Update an existing student
    ---
    tags:
      - Students
    parameters:
      - in: path
        name: student_id
        required: true
        type: integer
        description: ID of the student to update
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            age:
              type: integer
            branch:
              type: string
            phone:
              type: string
            status:
              type: string
    responses:
      200:
        description: Student updated successfully
      404:
        description: Student not found
    """
    student = Student.query.get(student_id)

    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON received"}), 400

    student.name = data.get("name", student.name)
    student.age = data.get("age", student.age)
    student.branch = data.get("branch", student.branch)
    student.phone = data.get("phone", student.phone)
    student.status = data.get("status", student.status)

    db.session.commit()

    return jsonify({
        "message": "Student updated successfully",
        "student": student.to_dict()
    })
#filter by branch or status
@app.route("/filter_students", methods=["GET"])
@login_required
def filter_students():
    """
    Filter students by branch and/or status
    ---
    tags:
      - Students
    parameters:
      - in: query
        name: branch
        type: string
        required: false
        description: Branch name
        example: Biotechnology
      - in: query
        name: status
        type: string
        required: false
        description: Student status
        example: Applied
    responses:
      200:
        description: Filtered list of students
    """
    branch = request.args.get("branch")   # e.g., ?branch=Biotech
    status = request.args.get("status")   # e.g., ?status=Active

    query = Student.query.filter_by(is_active=True)

    if branch:
        query = query.filter_by(branch=branch)
    if status:
        query = query.filter_by(status=status)

    students = query.all()
    return jsonify([s.to_dict() for s in students])
#search by email
@app.route("/search_student", methods=["GET"])
@login_required
def search_student():
    """
    Search student by email
    ---
    tags:
      - Students
    parameters:
      - in: query
        name: email
        required: true
        type: string
        description: Email address of the student
        example: rahul@example.com
    responses:
      200:
        description: Student found
      400:
        description: Email parameter is required
      404:
        description: Student not found
    """
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Email parameter is required"}), 400

    student = Student.query.filter_by(email=email, is_active=True).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(student.to_dict())
#for analytics
@app.route("/analytics", methods=["GET"])
@login_required
def analytics():
    """
    Get student analytics
    ---
    tags:
      - Analytics
    responses:
      200:
        description: Student analytics including counts and averages
    """
    students = Student.query.filter_by(is_active=True).all()

    total_active = len(students)
    
    # Count per branch
    branch_counts = {}
    for s in students:
        branch_counts[s.branch] = branch_counts.get(s.branch, 0) + 1

    # Count per status
    status_counts = {}
    for s in students:
        status_counts[s.status] = status_counts.get(s.status, 0) + 1

    # Average age
    ages = [s.age for s in students if s.age is not None]
    avg_age = sum(ages)/len(ages) if ages else 0
    
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_students = Student.query.filter(
        Student.created_at >= seven_days_ago,
        Student.is_active == True
    ).count()

    return jsonify({
        "total_active_students": total_active,
        "branch_counts": branch_counts,
        "status_counts": status_counts,
        "average_age": avg_age,
        "recently_added_last_7_days": recent_students
    })
@app.route("/export_students", methods=["GET"])
@login_required
def export_students():
    """
    Export active students as CSV
    ---
    tags:
      - Students
    produces:
      - text/csv
    responses:
      200:
        description: CSV file containing active students
    """
    students = Student.query.filter_by(is_active=True).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["ID", "Name", "Email", "Age", "Branch", "Status", "Created At"])

    for s in students:
        writer.writerow([s.id, s.name, s.email, s.age, s.branch, s.status, s.created_at])

    output.seek(0)

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=students.csv"}
    )
@app.route("/add_students_bulk", methods=["POST"])
@login_required
def add_students_bulk():
    """
    Add multiple students at once
    ---
    tags:
      - Students
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: array
          items:
            type: object
            properties:
              name:
                type: string
              email:
                type: string
              age:
                type: integer
              branch:
                type: string
              phone:
                type: string
              status:
                type: string
    responses:
      200:
        description: Bulk student addition completed
      400:
        description: Invalid request body
    """
    data = request.get_json()
    if not data or not isinstance(data, list):
        return jsonify({"error": "Send a list of students"}), 400

    added = []
    skipped = []

    for item in data:
        if not item.get("name") or not item.get("email"):
            skipped.append(item)
            continue
        existing = Student.query.filter_by(email=item["email"]).first()
        if existing:
            skipped.append(item)
            continue
        student = Student(
            name=item["name"],
            email=item["email"],
            age=item.get("age"),
            branch=item.get("branch"),
            phone=item.get("phone"),
            status=item.get("status", "Applied")
        )
        db.session.add(student)
        added.append(item["name"])

    db.session.commit()

    return jsonify({
        "message": f"{len(added)} students added",
        "added": added,
        "skipped": skipped
    })

if __name__ == "__main__":
    app.run(debug=True)





import os
import csv
import io
from flask import Response
from flask import Flask, request, jsonify
from models import db, Student

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return "Student Management System with Database Running"


@app.route("/add_student", methods=["POST"])
def add_student():
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
        status=data.get("status", "Applied")
    )

    db.session.add(student)
    db.session.commit()

    return jsonify({
        "message": "Student added successfully",
        "student": student.to_dict()
    })

@app.route("/students", methods=["GET"])
def view_students():
    students = Student.query.filter_by(is_active=True).all()
    return jsonify([s.to_dict() for s in students])

#  DELETE ROUTE 

@app.route("/delete_student/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
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
def update_student(student_id):
    student = Student.query.get(student_id)

    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON received"}), 400

    student.name = data.get("name", student.name)
    student.age = data.get("age", student.age)
    student.branch = data.get("branch", student.branch)
    student.status = data.get("status", student.status)

    db.session.commit()

    return jsonify({
        "message": "Student updated successfully",
        "student": student.to_dict()
    })
#filter by branch or status
@app.route("/filter_students", methods=["GET"])
def filter_students():
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
def search_student():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Email parameter is required"}), 400

    student = Student.query.filter_by(email=email, is_active=True).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(student.to_dict())
#for analytics
@app.route("/analytics", methods=["GET"])
def analytics():
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

    return jsonify({
        "total_active_students": total_active,
        "branch_counts": branch_counts,
        "status_counts": status_counts,
        "average_age": avg_age
    })
@app.route("/export_students", methods=["GET"])
def export_students():
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

if __name__ == "__main__":
    app.run(debug=True)





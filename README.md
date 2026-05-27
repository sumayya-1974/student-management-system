# Student Management System

This project was built to practice REST API development using Flask and SQLAlchemy while implementing real-world features like soft delete, filtering, validations, and analytics.

---

##  Tech Stack

- **Python** — Core language
- **Flask** — Web framework for building REST APIs
- **SQLAlchemy ORM** — Database interaction layer
- **SQLite** — Lightweight relational database
- **Postman** — API testing

---

##  Project Structure

```
student-management-system/
│
├── app.py          # All API routes and application logic
├── models.py       # Database model (Student table)
├── database.db     # Auto-generated SQLite database
├── .gitignore
└── README.md
```

---

##  How to Run Locally

**1. Clone the repository**
```bash
git clone https://github.com/sumayya-1974/student-management-system.git
cd student-management-system
```

**2. Install dependencies**
```bash
pip install flask flask-sqlalchemy
```

**3. Run the app**
```bash
python app.py
```

**4. Test the APIs using Postman**
> Base URL: `http://127.0.0.1:5000`

---

##  API Endpoints

###  Add a Student
**POST** `/add_student`

Request Body (JSON):
```json
{
  "name": "Arjun Nair",
  "email": "arjun.nair@example.com",
  "age": 22,
  "branch": "Biotech",
  "status": "Applied"
}
```

Response:
```json
{
  "message": "Student added successfully",
  "student": { "id": 1, "name": "Arjun Nair", "email": "arjun.nair@example.com" }
}
```

---

###  View All Active Students
**GET** `/students`

Response: List of all students where `is_active = true`

---

###  Update a Student
**PUT** `/update_student/<student_id>`

Request Body (JSON) — send only fields you want to update:
```json
{
  "status": "Active",
  "branch": "CSE"
}
```

---

###  Delete a Student (Soft Delete)
**DELETE** `/delete_student/<student_id>`

>  Business Rule: Students with status `"Active"` cannot be deleted. Change status first.


---

### 🔍 Search by Email
**GET** `/search_student?email=sumayya@example.com`

---

### 🔎 Filter by Branch or Status
**GET** `/filter_students?branch=Biotech`  
**GET** `/filter_students?status=Active`  
**GET** `/filter_students?branch=Biotech&status=Applied`

---

###  Analytics
**GET** `/analytics`

Response:
```json
{
  "total_active_students": 10,
  "branch_counts": { "Biotech": 4, "CSE": 6 },
  "status_counts": { "Applied": 3, "Active": 7 },
  "average_age": 21.5
}
```
### Export Students as CSV
- **GET** `/export_students`
- Download all active student records as a `.csv` file
- Opens directly in Excel or Google Sheets
---

##  What I Learned

- Building REST APIs using Flask
- Database modeling with SQLAlchemy
- Handling validations and business rules
- Working with JSON requests/responses
- Testing APIs using Postman
- Exporting student data as CSV files
- Storing timestamps for student records


---

##  Author

Developed by Sumayya  
[GitHub Profile](https://github.com/sumayya-1974)

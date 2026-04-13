from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# ---------------- MOCK DATA (Replace with DB later) ---------------- #
students = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
]

classes = [
    {"id": 1, "name": "Class A"},
    {"id": 2, "name": "Class B"}
]

tasks = [
    {"id": 1, "title": "Math Assignment", "student_id": 1, "status": "completed", "deadline": "2026-04-10"},
    {"id": 2, "title": "Science Project", "student_id": 1, "status": "pending", "deadline": "2026-04-15"},
    {"id": 3, "title": "History Essay", "student_id": 2, "status": "pending", "deadline": "2026-04-08"}
]

# ---------------- HELPER FUNCTIONS ---------------- #

def get_student_tasks(student_id):
    return [task for task in tasks if task["student_id"] == student_id]


def calculate_progress(student_id):
    student_tasks = get_student_tasks(student_id)
    if not student_tasks:
        return 0

    completed = len([t for t in student_tasks if t["status"] == "completed"])
    total = len(student_tasks)

    return round((completed / total) * 100, 2)


def get_overdue_tasks():
    today = datetime.today().date()
    overdue = []

    for task in tasks:
        deadline = datetime.strptime(task["deadline"], "%Y-%m-%d").date()
        if task["status"] != "completed" and deadline < today:
            overdue.append(task)

    return overdue

# ---------------- API ROUTES ---------------- #

@app.route("/dashboard/summary", methods=["GET"])
def dashboard_summary():
    total_students = len(students)
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t["status"] == "completed"])
    pending_tasks = total_tasks - completed_tasks

    return jsonify({
        "total_students": total_students,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks
    })


@app.route("/dashboard/student/<int:student_id>", methods=["GET"])
def student_dashboard(student_id):
    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    progress = calculate_progress(student_id)
    student_tasks = get_student_tasks(student_id)

    return jsonify({
        "student": student,
        "progress": progress,
        "tasks": student_tasks
    })


@app.route("/dashboard/overdue", methods=["GET"])
def overdue_tasks():
    return jsonify({
        "overdue_tasks": get_overdue_tasks()
    })


@app.route("/dashboard/class", methods=["GET"])
def class_dashboard():
    class_data = []

    for cls in classes:
        class_students = [s for s in students]
        avg_progress = 0

        if class_students:
            avg_progress = sum([calculate_progress(s["id"]) for s in class_students]) / len(class_students)

        class_data.append({
            "class": cls["name"],
            "average_progress": round(avg_progress, 2)
        })

    return jsonify(class_data)


# ---------------- RUN SERVER ---------------- #

if __name__ == "__main__":
    app.run(debug=True)

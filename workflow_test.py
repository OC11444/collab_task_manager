import json
from django.test import Client
from academic.models import Unit, Enrollment
from tasks.models import Task, TaskSubmission
from reports.models import UnitPerformanceSnapshot
from django.contrib.auth import get_user_model

User = get_user_model()
client = Client()

def run_workflow_test():
    print("🚀 Starting Master Integration Test...")

    # 1. AUTH CHECK
    print("🔑 Testing Auth Flow...")
    lecturer_payload = {"email": "lecturer_test@school.ac.ke", "password": "PasswordTest123!", "role": "lecturer"}
    student_payload = {"email": "james24.gitau@student.school.ac.ke", "password": "PasswordTest123!", "role": "student"}
    
    lec_resp = client.post('/api/users/login/', data=json.dumps(lecturer_payload), content_type='application/json')
    stu_resp = client.post('/api/users/login/', data=json.dumps(student_payload), content_type='application/json')
    
    if lec_resp.status_code != 200 or stu_resp.status_code != 200:
        print("❌ Auth Failed. Check credentials.")
        return

    lec_token = lec_resp.json()['tokens']['access']
    stu_token = stu_resp.json()['tokens']['access']
    print("✅ Auth Successful.")

    # 2. TASK CREATION
    print("📝 Testing Task Creation (Lecturer)...")
    unit = Unit.objects.get(code="CSD-301")
    task_payload = {
        "title": "Integration Test Task",
        "description": "Auto-generated test task",
        "due_date": "2026-12-31T23:59:59Z",
        "priority": "High",
        "unit": unit.id,
        "allow_late_submissions": False
    }
    task_resp = client.post('/api/v1/tasks/', data=json.dumps(task_payload), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {lec_token}')
    
    if task_resp.status_code != 201:
        print(f"❌ Task Creation Failed: {task_resp.content}")
        return
    
    task_id = task_resp.json()['id']
    print(f"✅ Task Created (ID: {task_id}).")

    # 3. STUDENT SUBMISSION (Cloud Link)
    print("☁️ Testing Cloud Link Submission (Student)...")
    sub_payload = {
        "task": task_id,
        "submission_link": "https://drive.google.com/test-link",
        "status": "done"
    }
    sub_resp = client.post('/api/v1/task-submissions/', data=json.dumps(sub_payload), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {stu_token}')
    
    if sub_resp.status_code != 201:
        print(f"❌ Submission Failed: {sub_resp.content}")
        return
    print("✅ Submission Successful.")

    # 4. REPORTING SNAPSHOT (MySQL Check)
    print("📊 Testing Reporting Snapshot (MySQL Aggregation)...")
    # We trigger the view to see if it handles the logic
    report_resp = client.get('/api/reports/dashboard/lecturer/', HTTP_AUTHORIZATION=f'Bearer {lec_token}')
    
    if report_resp.status_code == 200:
        print("✅ Reporting Dashboard Verified.")
        print(f"📊 Dashboard Rows Found: {len(report_resp.json())}")
    else:
        print(f"❌ Reporting Failed: {report_resp.content}")
        return

    print("\n🏆 WORKFLOW TEST PASSED: System is stable for deployment.")

run_workflow_test()
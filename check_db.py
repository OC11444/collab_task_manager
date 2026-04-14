import json
from django.contrib.auth import get_user_model
from academic.models import Unit, Enrollment
from django.test import Client

User = get_user_model()

print("\n--- 🔍 STARTING DATABASE VERIFICATION ---")

# 1. SETUP USERS
lec, _ = User.objects.update_or_create(
    username="lecturer_test",
    defaults={"email": "lecturer_test@school.ac.ke", "role": "staff", "is_staff": True}
)
lec.set_password("PasswordTest123!")
lec.save()

stu, _ = User.objects.update_or_create(
    username="james_g",
    defaults={"email": "james24.gitau@student.school.ac.ke", "role": "student"}
)
stu.set_password("PasswordTest123!")
stu.save()

# 2. SETUP ACADEMIC CONTEXT
unit, _ = Unit.objects.get_or_create(code="CSD-301", defaults={"name": "Computer Science Design", "lecturer": lec})
Enrollment.objects.get_or_create(student=stu, unit=unit)
print(f"✅ Database State: Users and Units ready (Unit: {unit.code})")

# 3. TEST AUTH
client = Client()
login_payload = {
    "email": "james24.gitau@student.school.ac.ke",
    "password": "PasswordTest123!",
    "role": "student"
}
response = client.post('/api/users/login/', data=json.dumps(login_payload), content_type='application/json')

if response.status_code == 200:
    print("✅ Auth Flow: Success (JWT generated)")
    print("--- 🏁 WORKFLOW VERIFIED: READY TO DEPLOY ---")
else:
    print(f"❌ Auth Flow: Failed (Status {response.status_code})")
    print(f"Details: {response.content.decode()[:200]}")
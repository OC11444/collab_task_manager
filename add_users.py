import csv
import os

# 1. The 10 new users to add
new_users = [
    {"email": "alice.w@student.school.ac.ke", "username": "alice_w", "role": "student", "registration_number": "STU-2026-010"},
    {"email": "bob.b@student.school.ac.ke", "username": "bob_b", "role": "student", "registration_number": "STU-2026-011"},
    {"email": "charlie.c@student.school.ac.ke", "username": "charlie_c", "role": "student", "registration_number": "STU-2026-012"},
    {"email": "diana.p@student.school.ac.ke", "username": "diana_p", "role": "student", "registration_number": "STU-2026-013"},
    {"email": "evan.e@student.school.ac.ke", "username": "evan_e", "role": "student", "registration_number": "STU-2026-014"},
    {"email": "fiona.f@student.school.ac.ke", "username": "fiona_f", "role": "student", "registration_number": "STU-2026-015"},
    {"email": "dr.brown@staff.school.ac.ke", "username": "brown_admin", "role": "staff", "registration_number": "EMP-99-010"},
    {"email": "prof.xavier@staff.school.ac.ke", "username": "xavier_prof", "role": "staff", "registration_number": "EMP-99-011"},
    {"email": "dr.strange@staff.school.ac.ke", "username": "strange_doc", "role": "staff", "registration_number": "EMP-99-012"},
    {"email": "prof.mcgonagall@staff.school.ac.ke", "username": "minerva_m", "role": "staff", "registration_number": "EMP-99-013"},
]

# 2. Path to your CSV file
file_path = "users/data/university_db.csv"

# 3. Append the new users
try:
    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["email", "username", "role", "registration_number"])
        writer.writerows(new_users)
    print(f"✅ Successfully added {len(new_users)} new users to {file_path}!")
except FileNotFoundError:
    print(f"❌ Error: Could not find {file_path}. Make sure you are running this from the project root!")
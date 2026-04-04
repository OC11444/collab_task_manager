# auth_logic.py

import json
import os
import re
import jwt
import datetime

USER_FILE = "users.json"
SECRET_KEY = "super-secret-task-manager-key" # Change this for production!

# --- STORAGE LOGIC ---
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as file:
            return json.load(file)
    return {"admin": "password123"} # Default starting user

def save_users(db):
    with open(USER_FILE, "w") as file:
        json.dump(db, file, indent=4)

users_db = load_users()
# --- VALIDATION LOGIC ---
def validate_inputs(username, password):
    if not username or not password:
        return False, "Fields cannot be empty."
    
    # Username: Alphanumeric only, 3-12 chars
    if not re.match(r"^[a-zA-Z0-9]{3,12}$", username):
        return False, "Username must be 3-12 letters/numbers."
        
    # Password: Minimum 6 characters
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
        
    return True, "Valid"

# --- AUTH LOGIC ---
def register(username, password):
    is_valid, msg = validate_inputs(username, password)
    if not is_valid:
        print(f"Registration Error: {msg}")
        return False

    if username in users_db:
        print("Error: User already exists.")
        return False

    users_db[username] = password
    save_users(users_db) # Permanently save to users.json
    print(f"Success: {username} registered!")
    return True

def login(username, password):
    if username in users_db and users_db[username] == password:
        # Create a JWT token (the "digital pass")
        payload = {
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        print("Login Successful! JWT Token generated.")
        return token
    else:
        print("Invalid credentials.")
        return None
    
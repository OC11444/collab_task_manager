# auth_logic.py

# A simple dictionary to simulate a database
users_db = {
    "admin": "password123",
    "brian": "project2026"
}

def login(username, password):
    if username in users_db:
        if users_db[username] == password:
            print(f"Welcome, {username}! Login successful.")
            return True
        else:
            print("Error: Incorrect password.")
            return False
    else:
        print("Error: User not found.")
        return False

# Quick test
if __name__ == "__main__":
    login("brian", "project2026")
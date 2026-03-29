# 🧠📋 Collaborative Task Manager

Welcome to the **Collaborative Task Manager** project 🤝. This guide will walk you through the initial setup to get your local development environment up and running ⚙️💻.

---

## 🚀 Developer Onboarding Guide

### 1. 📥 Clone the Repository
Download the project blueprints to your local machine and navigate into the project directory:

```bash
git clone <repository-url>
cd collab_task_manager
```

---

### 2. 🌿 Create a Feature Branch

To maintain a clean workflow 🧼, never work directly on the `main` or `dev` branches 🚫. Create a new branch for the specific feature you are building:

```bash
git checkout -b feature/your-feature-name
# Example: git checkout -b feature/submit-button
```

---

### 3. 🐍 Set Up the Virtual Environment

We use a virtual environment to keep dependencies isolated 🔒 and your system installation clean 🧹.

#### 💻 Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 🪟 Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

---

### 4. 📦 Install Dependencies

Install Django and all other required tools listed in the requirements file:

```bash
pip install -r requirements.txt
```

---

### 5. 🗄️ Build Your Local Database

For security reasons 🔐, the `db.sqlite3` file is not shared on GitHub. You must generate your own local database tables using the project migrations:

```bash
python manage.py migrate
```

---

### 6. 👤 Create Your Admin Account

Create a local superuser account to access the Django admin panel 🛠️. Follow the terminal prompts to set your username, email, and password:

```bash
python manage.py createsuperuser
```

---

### 7. ▶️ Run the Server

Start the local development server to see the project in action 🚀:

```bash
python manage.py runserver
```

Once the server is running, open your browser 🌐 and navigate to:

```
http://127.0.0.1:8000/admin
```

---

## 📁🚫 .gitignore

Create a file named `.gitignore` and paste the following:

```text
# 🐍 Python
__pycache__/
*.py[cod]
*$py.class
venv/
ENV/

# 🌐 Django
db.sqlite3
db.sqlite3-journal
media/
staticfiles/
.env

# 💻 OS-specific
.DS_Store
Thumbs.db
```

---

## 📦📝 requirements.txt

Create a file named `requirements.txt` and add the following:

```text
django>=4.2,<5.0
asgiref
sqlparse
```

---

## ✅✨ Notes

- 🌿 Always create a new feature branch before starting work
- 🔐 Never commit sensitive files like `.env` or `db.sqlite3`
- 🔄 Keep your dependencies updated in `requirements.txt`
- 🤝 Write clean, readable, and maintainable code

---

## 💡🔥 Pro Tip

Consistency in setup = fewer bugs 🐞 and smoother collaboration 🤝. Follow this guide exactly and your team will thank you later 😄

---

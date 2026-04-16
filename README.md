# 🧠📋 Collaborative Task Manager

Welcome to the Collaborative Task Manager project 🤝. This guide will walk you through the initial setup to get your local development environment up and running, explain our modular architecture, and outline our next steps ⚙️💻.

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

To maintain a clean workflow 🧼, never work directly on the main or dev branches 🚫. Create a new branch for the specific feature you are building:

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

Install Django, MySQL client, and all other required tools listed in the requirements file:

```bash
pip install -r requirements.txt
```

---

### 5. 🔐 Environment Variables (.env) Setup

**CRITICAL:** We do not commit secrets to GitHub. You must create your own local environment file.

#### Create the file:

Copy the provided template to create your local `.env` file:

```bash
cp .env.example .env
```

#### Generate a Secret Key:

Run this command in your terminal to generate a unique Django Secret Key, then copy and paste it into your `.env` file:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

#### Database Credentials:

Update the `DB_PASSWORD` in your `.env` file to match your local MySQL root password.

> Note: If on Mac/Linux, ensure `DB_UNIX_SOCKET` points to your correct MySQL socket (usually `/tmp/mysql.sock`).

---

### 6. 🗄️ Build Your Local Database (MySQL)

This project uses MySQL (not SQLite) to support advanced data aggregation.

Ensure your local MySQL server is running, then generate your local database tables:

```bash
python manage.py migrate
```

---

### 7. 👤 Create Your Admin Account

Create a local superuser account to access the Django admin panel 🛠️. Follow the terminal prompts:

```bash
python manage.py createsuperuser
```

---

### 8. ▶️ Run the Server

Start the local development server to see the project in action 🚀:

```bash
python manage.py runserver
```

Once the server is running, open your browser 🌐 and navigate to:

http://127.0.0.1:8000/admin

---

## 🏗️ Architecture & Module Flow

This project follows a **Modular Monolith pattern**. Apps should avoid directly importing models from other apps in order to reduce coupling.

### Core patterns

* **Selectors (`selectors.py`)**: Data fetching across app boundaries
* **Services (`services.py`)**: Business logic and workflows (e.g., creating snapshots)
* **Signals (`signals.py`)**: Cross-app notifications and event handling

### Current app responsibilities

* **Users module**: Authentication and role-aware access flows
* **Academic module**: Enrollment-aware access control for units and learning structure
* **Tasks module**: Assignment creation and submission management
* **Comments & Notifications module**: Collaboration feedback and alerts
* **Reports module**: Snapshot-based performance aggregation for dashboards

---

## 🧪 Integration Testing Lifecycle

Before pushing code, run our internal workflow test to ensure the lifecycle isn't broken:

```bash
python manage.py shell < check_db.py
```

### Platform flow

* **Users Module**: Handles authentication and user role validation
* **Academic Module**: Acts as the gatekeeper. Students should only interact with tasks for units they are enrolled in
* **Tasks Module**: Manages assignments. Submissions are checked against the student's enrollment before being accepted
* **Reports Module**: Aggregates platform data into snapshots to support efficient dashboard queries using MySQL aggregation

---

## ⏭️ Next Phase: API & Frontend Integration

With the backend structure in place, the next phase is frontend-facing API integration. Planned work includes:

* Mapping backend DRF endpoints into an Axios frontend service layer
* Handling JWT token-based authentication flows and interceptors on the client
* Binding JSON responses to UI components

---

## 🚀 CI/CD & Deployment

We use GitHub Actions for continuous integration.

Every push to dev or main triggers a pipeline that:

* Spins up a MySQL 9.0 container
* Injects database secrets
* Applies all migrations
* Runs automated tests

> All status checks must pass before merging changes.

---

## 📁🚫 .gitignore Reference

Ensure your `.gitignore` includes these core entries:

```plaintext
# 🐍 Python
__pycache__/
*.py[cod]
*$py.class
venv/

# 🌐 Environment & Backups
.env
*.sql

# 💻 OS-specific
.DS_Store
```

---

## 📦📝 requirements.txt Reference

Ensure your `requirements.txt` includes at least:

```plaintext
django>=4.2,<5.0
djangorestframework
djangorestframework-simplejwt
mysqlclient
python-dotenv
```

---

## 💡🔥 Notes & Pro Tips

* 🌿 Branching: Always create a new feature branch before starting work
* 💬 Comment the "Why": Explain reasoning behind complex logic
* ⚙️ Keep Secrets Safe: Never commit sensitive files like `.env`

> If you add a new external integration (like email delivery or object storage), add the blank variable name to `.env.example` so everyone on the team knows what needs to be configured! 🚀

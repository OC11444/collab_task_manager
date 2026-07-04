# 🧠 Collaborative Task Manager — Developer Onboarding Guide

Welcome to the Collaborative Task Manager project.

This document provides the exact setup steps required to run the system locally. Follow them precisely to avoid configuration issues (CORS, database access, or authentication failures).

---

## 🚀 1. Repository Setup

```bash
# Initial clone
git clone https://github.com/OC11444/collab_task_manager.git

# Enter project directory
cd collab_task_manager

# Pull latest updates (if already cloned)
git pull origin main
```

---

## 🔐 2. Environment Configuration (.env)

Create a `.env` file in the project root directory and configure it as follows:

```env
# =========================
# Django Core Configuration
# =========================
DEBUG=True
SECRET_KEY=your-generated-secret-key
ALLOWED_HOSTS=127.0.0.1 localhost .onrender.com

# =========================
# Database (MySQL)
# =========================
DB_NAME=collab_db
DB_USER=root
DB_PASSWORD=your_local_mysql_password
DB_HOST=localhost
DB_PORT=3306

# =========================
# Email Configuration
# =========================
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=
```

⚠️ If `EMAIL_BACKEND` is set to console, verification emails will appear in the terminal instead of being sent externally.

---

## 🗄️ 3. Backend Setup

### Install dependencies
```bash
pip install -r requirements.txt
```

### Generate Django secret key (optional)
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Run migrations
```bash
python manage.py migrate
```

### Create admin user
```bash
python manage.py createsuperuser
```

Admin panel:
```
http://127.0.0.1:8000/admin
```

---

## 🎨 4. Frontend Configuration

Update API base URL inside:

```
src/lib/api.ts
```

### Local Development
```ts
http://127.0.0.1:8000
```

### Production
```ts
https://academic-api-bfhv.onrender.com
```

---

## ▶️ Start Development Servers

### Backend
```bash
python manage.py runserver
```
Runs on:
```
http://127.0.0.1:8000
```

### Frontend
```bash
npm run dev
```
Runs on:
```
http://localhost:5173
```

---

## 🛠️ 5. System Constraints

### CORS Policy
- Allowed origins:
  - localhost:5173
  - localhost:8080
- Active only when `DEBUG=True`
- Disabling DEBUG blocks frontend communication

### Timezone
```
Africa/Nairobi
```

### Database Requirement
- MySQL only
- SQLite is not supported

---

## 🧪 6. Verification Flow

1. Register via frontend
2. Ensure email is captured in CSV (if applicable)
3. Check terminal for verification link (console email mode)
4. Open link in browser
5. Access Student/Staff dashboard

---

## ✅ Setup Complete

If all steps are followed correctly:
- Backend runs successfully on Django
- Frontend connects via API
- Authentication and verification flow works locally
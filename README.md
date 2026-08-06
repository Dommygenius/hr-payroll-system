# HRMS Pro — Enterprise Human Resource Management System

A modern, enterprise-grade HR and Payroll platform built with Django, designed for small, medium, and large organizations. Consolidates employee management, payroll, leave, recruitment, attendance, performance, and more into a single unified system.

## Features

### Core Modules
- **Employee Management** — Profiles, departments, branches, designations, contracts, documents, org structure
- **Recruitment & Onboarding** — Job postings, ATS, interviews, offer letters, digital onboarding
- **Payroll & Compliance** — Salary structures, allowances, deductions, tax, pension, payslips, approval workflows
- **Leave Management** — Leave types, balances, multi-level approvals, calendar, accrual
- **Time & Attendance** — Shifts, rosters, biometric/QR/geo integration, overtime tracking
- **Performance Management** — Goals, KPIs, reviews, 360° feedback
- **Employee Self-Service** — Profile updates, leave requests, payslip downloads
- **Reports & Analytics** — Dashboards, PDF/Excel export, interactive charts
- **Employee Relations** — Grievances, recognition, exit interviews
- **Disciplinary Management** — Incidents, warnings, suspensions, hearings
- **Casuals Management** — Daily wages, attendance, payments
- **Feedback & Surveys** — Anonymous surveys, engagement analytics

### AI Features
- Resume screening & candidate ranking
- Payroll anomaly detection
- Employee attrition prediction
- Attendance anomaly detection
- HR chatbot
- Smart report generation

### Security & Authentication
- Username/Email/Phone login
- OAuth (Google, Microsoft, GitHub)
- LDAP/Active Directory
- MFA/2FA (TOTP)
- JWT & API token authentication
- RBAC with permission groups
- Audit logs & session management
- Password policies & account lockout

### Enterprise Capabilities
- Multi-company, multi-branch, multi-country
- Multi-currency & multi-language
- API-first architecture with OpenAPI/Swagger docs
- Docker deployment with Nginx, Gunicorn, Celery
- CI/CD with GitHub Actions

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5, Django REST Framework |
| Database | PostgreSQL |
| Cache/Queue | Redis, Celery |
| Auth | JWT, django-allauth, django-otp |
| Frontend | Bootstrap 5, Chart.js |
| Server | Gunicorn, Nginx |
| Container | Docker, Docker Compose |

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 16+ (or SQLite for dev)
- Redis (optional for dev)

### Local Development

```bash
# Clone and setup
cd "HR & Payroll System"
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements/dev.txt

# Configure environment
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/Mac

# Run migrations and seed data
python manage.py migrate
python manage.py seed_data

# Start development server
python manage.py runserver
```

Visit **http://localhost:8000** and login with:
- **Email:** `admin@acme.com`
- **Password:** `Admin@123456`

### Docker Deployment

```bash
docker-compose up -d --build
```

Services:
- **Web:** http://localhost:8000
- **Nginx:** http://localhost:80
- **API Docs:** http://localhost:8000/api/docs/
- **Admin:** http://localhost:8000/admin/

## API Documentation

Interactive Swagger UI available at `/api/docs/` when the server is running.

### Authentication

```bash
# Obtain JWT token
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@acme.com", "password": "Admin@123456"}'

# Use token
curl http://localhost:8000/api/v1/employees/ \
  -H "Authorization: Bearer <access_token>"
```

### Key API Endpoints

| Module | Endpoint |
|--------|----------|
| Employees | `/api/v1/employees/` |
| Recruitment | `/api/v1/recruitment/job-postings/` |
| Payroll | `/api/v1/payroll/payroll-runs/` |
| Leave | `/api/v1/leave/leave-requests/` |
| Attendance | `/api/v1/attendance/attendance-records/` |
| Performance | `/api/v1/performance/reviews/` |
| AI Chatbot | `POST /api/v1/ai/chat/` |
| Reports | `/api/v1/reports/dashboard-stats/` |

## Project Structure

```
├── apps/
│   ├── accounts/       # Authentication, RBAC, audit logs
│   ├── core/           # Company, branch, department, base models
│   ├── employees/      # Employee profiles, contracts, documents
│   ├── recruitment/    # Job postings, ATS, onboarding
│   ├── payroll/        # Salary, payslips, loans
│   ├── leave/          # Leave types, requests, approvals
│   ├── attendance/     # Shifts, records, biometric devices
│   ├── performance/    # Goals, KPIs, reviews, 360 feedback
│   ├── relations/      # Grievances, recognition
│   ├── disciplinary/   # Incidents, warnings, hearings
│   ├── casuals/        # Casual worker management
│   ├── surveys/        # Employee surveys
│   ├── ai_features/    # AI services & chatbot
│   ├── integrations/   # ERP, payment, SMS integrations
│   ├── notifications/  # Email, SMS, push, in-app
│   ├── reports/        # Analytics & export
│   └── dashboard/      # Web UI dashboard
├── config/             # Django settings, URLs, Celery
├── templates/          # Bootstrap 5 templates
├── static/             # CSS, JS assets
├── nginx/              # Nginx configuration
├── requirements/       # Python dependencies
├── tests/              # Unit & integration tests
└── docker-compose.yml  # Container orchestration
```

## User Roles

| Role | Access |
|------|--------|
| Super Admin | Full system access |
| HR Administrator | HR modules management |
| Payroll Officer | Payroll processing |
| Recruiter | Recruitment module |
| Manager / Supervisor | Team management, approvals |
| Employee | Self-service portal |
| Finance Officer | Financial reports |
| Auditor | Read-only audit access |

## Running Tests

```bash
pytest
pytest --cov=apps --cov-report=html
```

## GitHub Auto-Push

This project is configured to **push automatically**:

| Trigger | Behavior |
|---------|----------|
| **After every git commit** | Post-commit hook pushes to `origin` |
| **After Cursor agent sessions** | Stop hook commits pending changes and pushes |

### One-time setup

1. Authenticate GitHub CLI:
   ```powershell
   gh auth login -h github.com
   ```

2. Create the remote repo and push:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_github.ps1
   ```

3. Install git hooks (if not already installed):
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/install_git_hooks.ps1
   ```

Manual push anytime:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/auto_push.ps1
```

## License

Proprietary — All rights reserved.

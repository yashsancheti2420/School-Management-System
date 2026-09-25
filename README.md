# SchoolSphere — School Management System

SchoolSphere is a Flask web application for managing students, teachers, staff, classes, subjects, and student promotions. It is ready to run locally, publish on GitHub, or deploy to Render.

## Features

- Student records: add, search, edit, delete, and promote students
- Teacher and staff record management
- Classes, sections, and subjects setup
- Dashboard totals and class-wise enrollment
- Promotion history report
- Responsive UI and deployment health check

## Run locally

Prerequisite: Python 3.10 or later.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Visit [http://127.0.0.1:5000](http://127.0.0.1:5000). The local database is created automatically as `schoolmanagement.db`; it is deliberately ignored by Git so student data is never published.

## Configuration

Copy `.env.example` to `.env` and set a secure `SECRET_KEY` before public deployment.

| Variable | Required in production | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | Yes | Protects Flask sessions and messages. |
| `APP_ENV` | Yes | Set to `production` for production security checks. |
| `DATABASE_PATH` | Recommended | Path for SQLite data; use a persistent disk on your host. |
| `PORT` | Host-provided | Port on which the service listens. |

## Deploy to Render

1. Create a GitHub repository and push this project.
2. In Render, choose **New → Blueprint** and select the repository.
3. Render reads `render.yaml`, installs dependencies, creates a persistent disk for data, and generates a production secret.
4. Check `https://your-service.onrender.com/health`; it should return `{"status":"ok"}`.

`Procfile` is included for other Procfile-based hosts. It runs one production worker, appropriate for this SQLite-backed application.

## Publish to GitHub

```powershell
git init
git add .
git commit -m "Initial release of SchoolSphere"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/schoolsphere.git
git push -u origin main
```

Before pushing, verify `.env` and any `*.db` files do not appear in `git status`. The included `.gitignore` protects secrets and student records.

## Project structure

- `app.py` — Flask routes, validation, and database access
- `main.py` — Local development entry point
- `schema.sql` — SQLite database schema
- `templates/` — HTML pages
- `static/` — CSS and browser JavaScript
- `render.yaml` — Render deployment blueprint
- `Procfile` — Generic production start command

## Database

`schema.sql` contains the requested `students`, `teachers`, `staff`, `classes`, `subjects`, and `student_history` tables. The project uses SQLite for simple, password-free deployment. For a high-traffic multi-user system handling real school data, migrate to managed PostgreSQL or MySQL.

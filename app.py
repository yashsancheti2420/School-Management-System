"""School Management System — Flask application."""
from __future__ import annotations
import os
import sqlite3
from datetime import date
from pathlib import Path
from flask import Flask, abort, flash, g, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent

# On Vercel, serverless containers have a read-only filesystem except for /tmp
if os.environ.get("VERCEL"):
    DEFAULT_DATABASE = Path("/tmp/schoolmanagement.db")
else:
    DEFAULT_DATABASE = BASE_DIR / "schoolmanagement.db"

# For deployment, set DATABASE_PATH to a persistent-disk location, for example
# /var/data/schoolmanagement.db on Render.
database_path = Path(os.environ.get("DATABASE_PATH", DEFAULT_DATABASE))
secret_key = os.environ.get("SECRET_KEY", "vercel-secret-key" if os.environ.get("VERCEL") else None)

if os.environ.get("APP_ENV") == "production" and not secret_key:
    raise RuntimeError("SECRET_KEY must be set when APP_ENV=production.")

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)
app.config.update(
    SECRET_KEY=secret_key or "local-development-only-change-me",
    DATABASE=database_path,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("APP_ENV") == "production",
)

ENTITY_CONFIG = {
 "students": {"title":"Students","singular":"Student","id":"student_id","fields":[("first_name","First name","text",True),("last_name","Last name","text",True),("gender","Gender","select",True,["Male","Female","Other"]),("date_of_birth","Date of birth","date",False),("phone","Phone","tel",False),("email","Email","email",False),("address","Address","textarea",False),("class","Class","text",True),("section","Section","text",True),("roll_number","Roll number","text",True),("admission_date","Admission date","date",False),("academic_year","Academic year","text",True),("status","Status","select",True,["Active","Inactive","Graduated"]) ]},
 "teachers": {"title":"Teachers","singular":"Teacher","id":"teacher_id","fields":[("first_name","First name","text",True),("last_name","Last name","text",True),("gender","Gender","select",True,["Male","Female","Other"]),("date_of_birth","Date of birth","date",False),("phone","Phone","tel",False),("email","Email","email",False),("address","Address","textarea",False),("subject","Subject","text",True),("qualification","Qualification","text",False),("joining_date","Joining date","date",False),("salary","Salary","number",False),("status","Status","select",True,["Active","Inactive","On Leave"]) ]},
 "staff": {"title":"Staff","singular":"Staff member","id":"staff_id","fields":[("first_name","First name","text",True),("last_name","Last name","text",True),("gender","Gender","select",True,["Male","Female","Other"]),("phone","Phone","tel",False),("email","Email","email",False),("address","Address","textarea",False),("role","Role","text",True),("joining_date","Joining date","date",False),("salary","Salary","number",False),("status","Status","select",True,["Active","Inactive","On Leave"]) ]},
 "classes": {"title":"Classes","singular":"Class","id":"class_id","fields":[("name","Class name","text",True),("section","Section","text",True),("academic_year","Academic year","text",True),("class_teacher","Class teacher","text",False)]},
 "subjects": {"title":"Subjects","singular":"Subject","id":"subject_id","fields":[("name","Subject name","text",True),("code","Subject code","text",True),("class_name","Class","text",False),("teacher","Assigned teacher","text",False)]},
}

def get_db():
    if "db" not in g:
        Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(app.config["DATABASE"]); g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db: db.close()

def initialize_database():
    """Create tables on application startup; the schema is idempotent."""
    db = get_db()
    db.executescript((BASE_DIR / "schema.sql").read_text(encoding="utf-8"))
    db.commit()

@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

def entity_or_404(entity):
    if entity not in ENTITY_CONFIG: abort(404)
    return ENTITY_CONFIG[entity]

def form_values(config):
    values = {}
    for field, _label, kind, required, *_ in config["fields"]:
        value = request.form.get(field, "").strip()
        if required and not value: raise ValueError(f"{field.replace('_', ' ').title()} is required.")
        if kind == "number" and value:
            try: float(value)
            except ValueError: raise ValueError("Salary must be a number.")
        values[field] = value or None
    return values

@app.route("/")
def dashboard():
    db = get_db()
    totals = {name: db.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0] for name in ("students", "teachers", "staff")}
    class_counts = db.execute("SELECT class, section, COUNT(*) total FROM students WHERE status='Active' GROUP BY class, section ORDER BY class, section").fetchall()
    recent = db.execute("SELECT * FROM students ORDER BY student_id DESC LIMIT 5").fetchall()
    return render_template("dashboard.html", totals=totals, class_counts=class_counts, recent=recent)

@app.get("/health")
def health_check():
    """Small endpoint used by hosting platforms to verify the app is alive."""
    get_db().execute("SELECT 1").fetchone()
    return {"status": "ok"}, 200

@app.route("/<entity>")
def list_records(entity):
    config = entity_or_404(entity); q = request.args.get("q", "").strip(); db = get_db()
    if q:
        cols = [field[0] for field in config["fields"] if field[2] != "textarea"]
        condition = " OR ".join(f"COALESCE({col}, '') LIKE ?" for col in cols)
        rows = db.execute(f"SELECT * FROM {entity} WHERE {condition} ORDER BY {config['id']} DESC", [f"%{q}%"] * len(cols)).fetchall()
    else: rows = db.execute(f"SELECT * FROM {entity} ORDER BY {config['id']} DESC").fetchall()
    return render_template("records.html", config=config, entity=entity, rows=rows, q=q)

@app.route("/<entity>/add", methods=["GET", "POST"])
def add_record(entity):
    config = entity_or_404(entity)
    if request.method == "POST":
        try:
            values = form_values(config); cols = list(values)
            get_db().execute(f"INSERT INTO {entity} ({', '.join(cols)}) VALUES ({', '.join('?' for _ in cols)})", list(values.values())); get_db().commit()
            flash(f"{config['singular']} added successfully.", "success"); return redirect(url_for("list_records", entity=entity))
        except (ValueError, sqlite3.IntegrityError) as error: flash(str(error), "error")
    return render_template("form.html", config=config, entity=entity, record=None, today=date.today().isoformat())

@app.route("/<entity>/<int:record_id>/edit", methods=["GET", "POST"])
def edit_record(entity, record_id):
    config = entity_or_404(entity); db = get_db(); record = db.execute(f"SELECT * FROM {entity} WHERE {config['id']}=?", (record_id,)).fetchone()
    if not record: abort(404)
    if request.method == "POST":
        try:
            values = form_values(config); assignments = ", ".join(f"{key}=?" for key in values)
            db.execute(f"UPDATE {entity} SET {assignments} WHERE {config['id']}=?", [*values.values(), record_id]); db.commit()
            flash(f"{config['singular']} updated successfully.", "success"); return redirect(url_for("list_records", entity=entity))
        except (ValueError, sqlite3.IntegrityError) as error: flash(str(error), "error")
    return render_template("form.html", config=config, entity=entity, record=record, today=date.today().isoformat())

@app.post("/<entity>/<int:record_id>/delete")
def delete_record(entity, record_id):
    config = entity_or_404(entity); db = get_db(); db.execute(f"DELETE FROM {entity} WHERE {config['id']}=?", (record_id,)); db.commit()
    flash(f"{config['singular']} removed.", "success"); return redirect(url_for("list_records", entity=entity))

@app.route("/students/<int:student_id>/promote", methods=["GET", "POST"])
def promote_student(student_id):
    db = get_db(); student = db.execute("SELECT * FROM students WHERE student_id=?", (student_id,)).fetchone()
    if not student: abort(404)
    if request.method == "POST":
        new_class, new_section, new_year = (request.form.get(k, "").strip() for k in ("class", "section", "academic_year"))
        if not all((new_class, new_section, new_year)): flash("Class, section, and academic year are required.", "error")
        else:
            db.execute("INSERT INTO student_history (student_id,previous_class,previous_section,previous_academic_year,promoted_to_class,promoted_to_section,new_academic_year,promotion_date) VALUES (?,?,?,?,?,?,?,?)", (student_id,student["class"],student["section"],student["academic_year"],new_class,new_section,new_year,date.today().isoformat()))
            db.execute("UPDATE students SET class=?, section=?, academic_year=? WHERE student_id=?", (new_class,new_section,new_year,student_id)); db.commit()
            flash("Student promoted and history recorded.", "success"); return redirect(url_for("list_records", entity="students"))
    return render_template("promote.html", student=student)

@app.route("/reports")
def reports():
    promotions = get_db().execute("SELECT h.*,s.first_name,s.last_name FROM student_history h JOIN students s ON s.student_id=h.student_id ORDER BY h.promotion_date DESC").fetchall()
    return render_template("reports.html", promotions=promotions)


with app.app_context():
    initialize_database()

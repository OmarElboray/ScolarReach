"""
ScolarReach - MVP Backend + Frontend (Steps 1 & 2)
====================================================
Single-file Flask + SQLite prototype.
Templates live in ./templates/ and extend base.html.

Run:
    pip install flask
    python app.py
    → http://127.0.0.1:5000
"""

import sqlite3
import hashlib
import os
from functools import wraps
from flask import (
    Flask, g, session, request, redirect,
    url_for, render_template, flash, abort
)

# ---------------------------------------------------------------------------
# App Configuration
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")

DATABASE = "scolarreach.db"


# ---------------------------------------------------------------------------
# Database Helpers
# ---------------------------------------------------------------------------

def get_db() -> sqlite3.Connection:
    """Open a database connection scoped to the current request (via Flask g)."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row   # rows behave like dicts
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    """Close the database connection at the end of every request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create all tables if they don't already exist."""
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE,
            role          TEXT    NOT NULL CHECK(role IN ('student', 'mentor')),
            password_hash TEXT    NOT NULL,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS projects (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            title         TEXT    NOT NULL,
            description   TEXT,
            domain        TEXT,
            status        TEXT    NOT NULL DEFAULT 'open'
                              CHECK(status IN ('open', 'in_progress', 'completed', 'cancelled')),
            created_by_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- ----------------------------------------------------------------
        -- applications table  (Step 3)
        -- ----------------------------------------------------------------
        CREATE TABLE IF NOT EXISTS applications (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id       INTEGER NOT NULL REFERENCES users(id)    ON DELETE CASCADE,
            project_id       INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            mentor_id        INTEGER          REFERENCES users(id)    ON DELETE SET NULL,
            status           TEXT    NOT NULL DEFAULT 'pending'
                                 CHECK(status IN ('pending', 'accepted', 'rejected')),
            application_text TEXT    NOT NULL,
            created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, project_id)
        );
    """)
    db.commit()


# ---------------------------------------------------------------------------
# Password Utilities
# ---------------------------------------------------------------------------

def hash_password(plain: str) -> str:
    """SHA-256 hash (MVP only — use bcrypt/argon2 in production)."""
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed


# ---------------------------------------------------------------------------
# Auth Decorators
# ---------------------------------------------------------------------------

def login_required(f):
    """Redirect to /login if the user is not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """Abort with 403 if the logged-in user doesn't hold one of the given roles."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get("role") not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator


# ---------------------------------------------------------------------------
# Route: Home  (GET /)
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Route: Register  (GET / POST /register)
# ---------------------------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name     = request.form.get("name", "").strip()
    email    = request.form.get("email", "").strip().lower()
    role     = request.form.get("role", "").strip()
    password = request.form.get("password", "")

    errors = []
    if not name:
        errors.append("Name is required.")
    if not email:
        errors.append("Email is required.")
    if role not in ("student", "mentor"):
        errors.append("Please select a role.")
    if len(password) < 6:
        errors.append("Password must be at least 6 characters.")

    if errors:
        return render_template("register.html", errors=errors)

    db = get_db()
    if db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone():
        return render_template("register.html", errors=["That email is already registered."])

    db.execute(
        "INSERT INTO users (name, email, role, password_hash) VALUES (?, ?, ?, ?)",
        (name, email, role, hash_password(password))
    )
    db.commit()

    flash("Account created — please sign in.", "success")
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Route: Login  (GET / POST /login)
# ---------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email    = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    db   = get_db()
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    if not user or not verify_password(password, user["password_hash"]):
        return render_template("login.html", error="Invalid email or password.")

    session.clear()
    session["user_id"] = user["id"]
    session["role"]    = user["role"]
    session["name"]    = user["name"]

    return redirect(url_for("dashboard"))


# ---------------------------------------------------------------------------
# Route: Logout  (GET /logout)
# ---------------------------------------------------------------------------

@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You've been signed out.", "success")
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Route: Dashboard  (GET /dashboard)
# ---------------------------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    db   = get_db()
    role = session["role"]

    if role == "student":
        projects = db.execute(
            """
            SELECT p.id, p.title, p.description, p.domain, p.status, p.created_at
            FROM   projects p
            WHERE  p.created_by_id = ?
            ORDER  BY p.created_at DESC
            """,
            (session["user_id"],)
        ).fetchall()

        return render_template(
            "dashboard_student.html",
            user_name=session["name"],
            projects=[dict(row) for row in projects],
        )

    elif role == "mentor":
        projects = db.execute(
            """
            SELECT p.id, p.title, p.description, p.domain, p.status,
                   p.created_at, u.name AS student_name
            FROM   projects p
            JOIN   users    u ON u.id = p.created_by_id
            WHERE  p.status IN ('open', 'in_progress')
            ORDER  BY p.created_at DESC
            """
        ).fetchall()

        return render_template(
            "dashboard_mentor.html",
            user_name=session["name"],
            projects=[dict(row) for row in projects],
        )

    abort(403)


# ---------------------------------------------------------------------------
# Route: Add Project  (GET / POST /projects/new)
# ---------------------------------------------------------------------------

@app.route("/projects/new", methods=["GET", "POST"])
@login_required
@role_required("student")
def new_project():
    if request.method == "GET":
        return render_template("new_project.html")

    title       = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    domain      = request.form.get("domain", "").strip()

    errors = []
    if not title:
        errors.append("Project title is required.")
    if not domain:
        errors.append("Research domain is required.")

    if errors:
        return render_template("new_project.html", errors=errors)

    db = get_db()
    db.execute(
        """
        INSERT INTO projects (title, description, domain, status, created_by_id)
        VALUES (?, ?, ?, 'open', ?)
        """,
        (title, description, domain, session["user_id"])
    )
    db.commit()

    flash("Project submitted successfully!", "success")
    return redirect(url_for("dashboard"))


# ---------------------------------------------------------------------------
# Route: Project Detail  (GET /projects/<id>)  — enriched in Step 3
# ---------------------------------------------------------------------------

@app.route("/projects/<int:project_id>")
@login_required
def project_detail(project_id: int):
    db      = get_db()
    project = db.execute(
        """
        SELECT p.*, u.name AS student_name, u.email AS student_email
        FROM   projects p
        JOIN   users    u ON u.id = p.created_by_id
        WHERE  p.id = ?
        """,
        (project_id,)
    ).fetchone()

    if not project:
        abort(404)

    # Students may only view their own projects
    if session["role"] == "student" and project["created_by_id"] != session["user_id"]:
        abort(403)

    # ── Fetch application context depending on role ──────────────────────────
    user_application = None   # student's own application on this project
    applications     = []     # all applications visible to a mentor

    if session["role"] == "student":
        row = db.execute(
            "SELECT * FROM applications WHERE student_id = ? AND project_id = ?",
            (session["user_id"], project_id)
        ).fetchone()
        user_application = dict(row) if row else None

    elif session["role"] == "mentor":
        rows = db.execute(
            """
            SELECT a.*, u.name AS student_name, u.email AS student_email
            FROM   applications a
            JOIN   users        u ON u.id = a.student_id
            WHERE  a.project_id = ?
            ORDER  BY a.created_at ASC
            """,
            (project_id,)
        ).fetchall()
        applications = [dict(r) for r in rows]

    return render_template(
        "project_detail.html",
        project=dict(project),
        user_application=user_application,
        applications=applications,
    )


# ---------------------------------------------------------------------------
# Route: Apply for Mentorship  (POST /apply/<project_id>)  — Step 3
# ---------------------------------------------------------------------------

@app.route("/apply/<int:project_id>", methods=["POST"])
@login_required
@role_required("student")
def apply(project_id: int):
    db = get_db()

    project = db.execute(
        "SELECT * FROM projects WHERE id = ?", (project_id,)
    ).fetchone()

    if not project:
        abort(404)

    if project["status"] != "open":
        flash("This project is no longer accepting applications.", "error")
        return redirect(url_for("project_detail", project_id=project_id))

    if project["created_by_id"] == session["user_id"]:
        flash("You cannot apply to your own project.", "error")
        return redirect(url_for("project_detail", project_id=project_id))

    application_text = request.form.get("application_text", "").strip()
    if not application_text:
        flash("Please write a short application message before submitting.", "error")
        return redirect(url_for("project_detail", project_id=project_id))

    existing = db.execute(
        "SELECT id FROM applications WHERE student_id = ? AND project_id = ?",
        (session["user_id"], project_id)
    ).fetchone()
    if existing:
        flash("You have already applied to this project.", "error")
        return redirect(url_for("project_detail", project_id=project_id))

    db.execute(
        "INSERT INTO applications (student_id, project_id, application_text) VALUES (?, ?, ?)",
        (session["user_id"], project_id, application_text)
    )
    db.commit()

    flash("Application submitted! A mentor will review your request soon.", "success")
    return redirect(url_for("project_detail", project_id=project_id))


# ---------------------------------------------------------------------------
# Route: Review Application  (POST /application/review/<app_id>/<action>)
#                                                               — Step 3
# ---------------------------------------------------------------------------

@app.route("/application/review/<int:app_id>/<string:action>", methods=["POST"])
@login_required
@role_required("mentor")
def review_application(app_id: int, action: str):
    if action not in ("accept", "reject"):
        abort(400)

    db      = get_db()
    app_row = db.execute(
        """
        SELECT a.*, p.status AS project_status, p.id AS pid
        FROM   applications a
        JOIN   projects     p ON p.id = a.project_id
        WHERE  a.id = ?
        """,
        (app_id,)
    ).fetchone()

    if not app_row:
        abort(404)

    if app_row["status"] != "pending":
        flash("This application has already been reviewed.", "error")
        return redirect(url_for("project_detail", project_id=app_row["pid"]))

    if action == "accept":
        # Accept this application and record the mentor
        db.execute(
            "UPDATE applications SET status = 'accepted', mentor_id = ? WHERE id = ?",
            (session["user_id"], app_id)
        )
        # Auto-reject every other pending application on the same project
        db.execute(
            """
            UPDATE applications
            SET    status = 'rejected'
            WHERE  project_id = ? AND id != ? AND status = 'pending'
            """,
            (app_row["pid"], app_id)
        )
        # Advance project to in_progress (matched)
        db.execute(
            "UPDATE projects SET status = 'in_progress' WHERE id = ?",
            (app_row["pid"],)
        )
        db.commit()
        flash("Application accepted — the project is now In Progress. 🎉", "success")

    else:
        db.execute(
            "UPDATE applications SET status = 'rejected' WHERE id = ?",
            (app_id,)
        )
        db.commit()
        flash("Application declined.", "success")

    return redirect(url_for("project_detail", project_id=app_row["pid"]))


# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------

@app.errorhandler(403)
def forbidden(e):
    return render_template("errors/403.html"), 403


@app.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404


# ---------------------------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    with app.app_context():
        init_db()
        print("✅  Database initialised → scolarreach.db")
    app.run(debug=True, port=5000)

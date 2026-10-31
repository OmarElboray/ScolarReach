# ScolarReach

ScolarReach is a Flask and SQLite platform that connects student researchers with mentors. Students can propose projects, while mentors can discover opportunities and manage applications.

## Features

- Separate student and mentor workflows.
- Account registration and session-based authentication.
- Research project creation and discovery.
- Applications with pending, accepted, and rejected states.
- SQLite database initialized automatically by the application.
- Server-rendered HTML templates with Tailwind CSS and custom styling.

## Run locally

1. Clone the repository:

   ```bash
   git clone https://github.com/OmarElboray/ScolarReach.git
   cd ScolarReach
   ```

2. Install the dependency:

   ```bash
   pip install flask
   ```

3. Set a production secret when deploying:

   ```bash
   export SECRET_KEY="replace-with-a-random-secret"
   ```

4. Start the server:

   ```bash
   python app.py
   ```

Visit <http://127.0.0.1:5000>.

## Project structure

```text
ScolarReach/
├── app.py                       # Flask routes, authentication, and database setup
└── templates/
    ├── base.html
    ├── login.html
    ├── register.html
    ├── dashboard_student.html
    ├── dashboard_mentor.html
    ├── new_project.html
    └── project_detail.html
```

## Important security note

This is an MVP. The default development secret must be replaced, and the current password hashing implementation should be upgraded to a password-hashing algorithm such as Argon2 or bcrypt before production use.

## Status

ScolarReach is an early prototype. Email notifications, richer profiles, and data export are natural next steps.

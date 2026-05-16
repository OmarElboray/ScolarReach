# 🎓 ScolarReach

> **Bridging the gap between ambitious high school researchers and academic mentors.**

ScolarReach is a lightweight, role-based platform designed to democratize access to academic research. It provides a streamlined ecosystem where students can pitch research proposals and university-level mentors can discover, review, and accept ambitious young talent.

![Status](https://img.shields.io/badge/Status-Beta_MVP-amber)
![Python](https://img.shields.io/badge/Python-Flask-3776AB?logo=python&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-CDN-38B2AC?logo=tailwind-css&logoColor=white)
![Database](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)

---

## ✨ Key Features

* **Role-Based Architecture:** Distinct workflows, dashboards, and permissions for `Student` and `Mentor` profiles.
* **Frictionless Pitching:** Students can easily draft and submit structured research proposals across various STEM domains.
* **Live Discovery:** Mentors utilize a lightweight, dependency-free JavaScript live-filter to search projects by domain, status, or keyword instantly.
* **Application Engine:** A secure SQLite backend handling the full lifecycle of student-mentor matchmaking (Pending, Accepted, Rejected).
* **"Editorial" UI/UX:** Built with pure HTML5 and Tailwind CSS utility classes. Features custom typography (Playfair Display & DM Sans) and native CSS staggered entry animations for a premium, distraction-free feel.

## 🛠️ Tech Stack

ScolarReach was intentionally built as a lightweight, modular monolith to prioritize speed, maintainability, and clean architecture over framework bloat.

* **Backend:** Python, Flask
* **Database:** SQLite (Relational Data Modeling)
* **Frontend:** HTML5, Jinja2 Templating, Tailwind CSS (via CDN)
* **Styling:** Custom CSS Keyframes, Google Fonts

## 🚀 Local Installation

To run the ScolarReach MVP locally on your machine:

**1. Clone the repository**
```bash
git clone [https://github.com/OmarElboray/ScolarReach.git](https://github.com/OmarElboray/ScolarReach.git)
cd ScolarReach
```

**2. Install dependencies**
Ensure you have Python installed, then install Flask:
```bash
pip install flask
```

**3. Run the application**
The SQLite database will automatically initialize on the first run.
```bash
python app.py
```
*The app will be live at `http://127.0.0.1:5000`*

## 📁 Architecture Overview

```text
ScolarReach/
├── app.py                      # Core Flask routing, Auth logic, and DB initialization
└── templates/
    ├── base.html               # Master layout, Tailwind config, and global UI tokens
    ├── login.html              # Authentication
    ├── register.html           # Role-based onboarding
    ├── dashboard_student.html  # Application tracking & project creation access
    ├── dashboard_mentor.html   # Live-filtering project discovery grid
    ├── new_project.html        # Pitch submission form
    ├── project_detail.html     # Dynamic view for applications and mentor actions
    └── errors/                 # Graceful fallback UI
```

## 🗺️ Future Roadmap

As ScolarReach moves beyond the MVP phase, planned features include:
- [ ] **Flask-Mail Integration:** Automated email notifications for application status updates.
- [ ] **User Profiles:** Expanded profile pages showcasing past research and academic credentials.
- [ ] **Data Export:** Allowing mentors to export matched student cohorts to CSV.

## 👨‍💻 Author

**Omar Elboray**
* Grade 11 STEM Student & Developer specializing in AI-Integrated Biomedicine.
* LinkedIn: [omar-elboray](https://www.linkedin.com/in/omar-elboray-1309b7354/)

---
*Built for the future of frugal science and accessible research.*

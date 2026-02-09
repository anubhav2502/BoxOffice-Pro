# 🎬 BoxOffice Pro - Movie Ticket Booking System

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![Flask](https://img.shields.io/badge/Framework-Flask-green?style=flat&logo=flask)
![MySQL](https://img.shields.io/badge/Database-MySQL-orange?style=flat&logo=mysql)

**BoxOffice Pro** is a robust, full-stack web application designed to digitize and automate the movie ticket booking process. Built using **Python (Flask)** and **MySQL**, it features a **Three-Tier Architecture** that segregates duties between Administrators, Technical Staff, and Customers.

This project demonstrates the implementation of **Agile User Stories**, **Role-Based Access Control (RBAC)**, and **Database Transaction Management**.

---

## 🚀 Key Features

### 1. 👤 Customer Module
* **User Authentication:** Secure Signup and Login with session management.
* **Smart Search:** Filter movies by Language, Category, and Release Date.
* **Ticket Booking:** Real-time seat availability checks.
* **Booking History:** Dashboard to view past and upcoming bookings.
* **Cancellation:** Ability to cancel tickets with automatic seat inventory updates.

### 2. 🛠️ Admin Module (Management)
* **Content Management:** Add and Delete movie details.
* **Theater Management:** Onboard new theaters and manage pricing/capacity.
* **Dashboard:** Overview of active movies and registered theaters.

### 3. ⚙️ Tech Admin Module (Operations)
* **Scheduling:** Map specific movies to theaters for specific dates and times.
* **Inventory Control:** View and Delete active schedules.

---

## 📂 Project Structure and Architecture



The application follows the **Flask Blueprint Pattern**, dividing the system into functional modules for better maintainability.

```text
BoxOffice Pro/
├── 📁 admin/                  # Admin Management Logic
├── 📁 auth/                   # Security & Authentication
├── 📁 customer/               # Booking & History Logic
├── 📁 tech_admin/             # Scheduling Operations
├── 📁 static/                 # CSS (Modern UI) & JS
├── 📁 templates/              # Jinja2 HTML Templates
├── 🐍 app.py                  # Main Entry Point
├── 🐍 db.py                   # MySQL Connection Manager
├── 📄 requirements.txt        # Required Packages
└── 📄 test.txt                # Testing Guide & Credentials
🛠️ Installation and Setup
1. Prerequisites
Python 3.x and MySQL Server installed.

2. Database Setup
Run the script found in DB-documents/script.sql in your MySQL environment.

Update the credentials (User/Password) in db.py to match your local setup.

3. Environment Setup
Bash
# Create and activate virtual environment
python -m venv env
env\Scripts\activate   # For Windows

# Install dependencies
pip install -r requirements.txt
4. Run the App
Bash
python app.py
Access the app at: http://127.0.0.1:5000/

🧪 Testing the Application
After completing the setup, please refer to the test.txt file in the root directory.

This file contains:

Pre-configured Credentials for Admin, Tech Admin, and Customer roles.

Test Scenarios to verify Movie Addition, Scheduling, and Booking flows.

Step-by-step instructions to validate the seat inventory logic.

👨‍💻 Developed By
Anubhav Sharma - Full Stack Developer



├── 📁 DB-documents
│   └── 📄 script.sql
├── 📁 admin
│   ├── 🐍 __init__.py
│   ├── 🐍 routes.py
│   └── 🐍 service.py
├── 📁 auth
│   ├── 🐍 __init__.py
│   └── 🐍 routes.py
├── 📁 customer
│   ├── 🐍 __init__.py
│   ├── 🐍 routes.py
│   └── 🐍 service.py
├── 📁 static
│   ├── 🎨 auth.css
│   ├── 🎨 change_password.css
│   ├── 🎨 login.css
│   ├── 🎨 signup.css
│   └── 🎨 style.css
├── 📁 tech_admin
│   ├── 🐍 __init__.py
│   ├── 🐍 routes.py
│   └── 🐍 services.py
├── 📁 templates
│   ├── 📁 admin
│   │   ├── 🌐 add_movie.html
│   │   ├── 🌐 add_theater.html
│   │   ├── 🌐 delete_movie.html
│   │   ├── 🌐 home.html
│   │   ├── 🌐 view_movie.html
│   │   └── 🌐 view_theater.html
│   ├── 📁 auth
│   │   ├── 🌐 change_password.html
│   │   ├── 🌐 login.html
│   │   └── 🌐 signup.html
│   ├── 📁 customer
│   │   ├── 🌐 book_ticket.html
│   │   ├── 🌐 cancel_booking.html
│   │   ├── 🌐 history.html
│   │   └── 🌐 home.html
│   ├── 📁 tech_admin
│   │   ├── 🌐 delete_schedule.html
│   │   ├── 🌐 home.html
│   │   ├── 🌐 schedule_movie.html
│   │   └── 🌐 view_schedule.html
│   ├── 🌐 base.html
│   └── 🌐 index.html
├── 🐍 app.py
├── 🐍 db.py
├── 📝 readme.md
├── 📄 requirements.txt
└── 📄 test.txt
```

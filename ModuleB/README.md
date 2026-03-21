# IITGN Connect — College Social Media Platform

**CS 432 Databases | Assignment 2 - Module B**
**Indian Institute of Technology, Gandhinagar**

---

## Project Overview

IITGN Connect is a full-stack college social media platform built with **React** (frontend) and **Flask** (backend) using **MySQL** with raw SQL queries (no ORM). It features user authentication with email OTP verification, role-based access control (RBAC), group management, job postings, polls, attendance tracking, and comprehensive audit logging.

---

## Tech Stack

| Layer    | Technology                              |
| -------- | --------------------------------------- |
| Frontend | React 19, Vite 8, React Router 7       |
| Backend  | Flask, Flask-JWT-Extended, Flask-CORS   |
| Database | MySQL 8.0+                              |
| Auth     | JWT (JSON Web Tokens), bcrypt, Email OTP |
| Email    | Gmail SMTP (python-dotenv)              |

---

## Prerequisites

Make sure the following are installed on your machine:

- **Python 3.10+** — [python.org/downloads](https://www.python.org/downloads/)
- **MySQL 8.0+** — [dev.mysql.com/downloads](https://dev.mysql.com/downloads/mysql/)
- **Node.js 18+** and **npm** — [nodejs.org](https://nodejs.org/)
- **Git** (optional, for cloning)

---

## Project Structure

```
Databases Ass2/
├── app/
│   ├── backend/            # Flask API server
│   │   ├── app.py          # Entry point (port 5001)
│   │   ├── config.py       # DB + SMTP configuration
│   │   ├── db.py           # MySQL query helpers
│   │   ├── seed.py         # Database schema + sample data
│   │   ├── audit.py        # Audit logging (file + DB)
│   │   ├── email_service.py# OTP email service
│   │   ├── benchmark.py    # Performance benchmarking script
│   │   ├── .env            # Environment variables (SMTP, DB)
│   │   ├── routes/         # API route blueprints
│   │   │   ├── auth.py     # Login, register, OTP, forgot password
│   │   │   ├── posts.py    # Posts, comments, likes
│   │   │   ├── groups.py   # Groups, memberships, approvals
│   │   │   ├── jobs.py     # Job postings, referrals
│   │   │   ├── polls.py    # Polls and voting
│   │   │   ├── attendance.py # Class & mess attendance
│   │   │   ├── profile.py  # User profiles, claims
│   │   │   ├── members.py  # Member search
│   │   │   ├── admin.py    # Admin dashboard (RBAC protected)
│   │   │   └── settings.py # Profile settings, password, username
│   │   ├── uploads/        # User-uploaded images
│   │   └── benchmarks/     # Generated benchmark charts
│   │
│   └── iitgn-connect/      # React frontend
│       ├── src/
│       │   ├── pages/      # All page components
│       │   ├── components/ # Reusable UI components
│       │   ├── contexts/   # Auth context provider
│       │   ├── api.js      # Centralized API helper
│       │   └── App.jsx     # Route definitions
│       ├── package.json
│       └── vite.config.js
│
├── logs/                   # Audit log files
│   └── audit.log
├── sql/                    # SQL files
│   ├── schema.sql          # All CREATE TABLE statements
│   └── indexes.sql         # Performance indexes
├── report.ipynb            # Optimization report (Jupyter notebook)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## Setup Instructions

### Step 1: Clone / Copy the Project

```bash
# If using git
git clone <repo-url>
cd "Databases Ass2"

# Or copy the project folder to your machine
```

### Step 2: Start MySQL

Make sure MySQL is running on your machine:

```bash
# macOS (Homebrew)
brew services start mysql

# Ubuntu/Debian
sudo systemctl start mysql

# Windows — Start MySQL from Services or MySQL Workbench
```

### Step 3: Backend Setup

```bash
# 1. Create a Python virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate          # macOS / Linux
# OR
venv\Scripts\activate             # Windows (Command Prompt)
# OR
venv\Scripts\Activate.ps1         # Windows (PowerShell)

# 3. Install Python dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Edit `app/backend/.env` with your MySQL and SMTP credentials:

```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=root
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=anonymous.cse.iitgn@gmail.com
SMTP_PASSWORD=<gmail-app-password>
```

> **Note:** If your MySQL uses different credentials, update `MYSQL_USER` and `MYSQL_PASSWORD` accordingly.

> **Note:** For Gmail SMTP, you need a [Google App Password](https://support.google.com/accounts/answer/185833) (not your regular Gmail password). OTP-based features (registration, forgot password) require valid SMTP credentials.

### Step 5: Seed the Database

This creates all 22 tables and populates them with sample data:

```bash
cd app/backend
python seed.py
```

You should see output confirming table creation and data insertion.

### Step 6: Start the Backend Server

```bash
# From app/backend/
python app.py
```

The API server starts at **http://localhost:5001**. You should see:

```
 * Running on http://127.0.0.1:5001
```

### Step 7: Frontend Setup (New Terminal)

```bash
# From the project root
cd app/iitgn-connect

# Install Node dependencies
npm install

# Start the development server
npm run dev
```

The frontend starts at **http://localhost:5173**.

### Step 8: Open the App

Open **http://localhost:5173** in your browser. You're all set!

---

## Default Login Credentials

All seed users share the same password: **`password123`**

| Username        | Name                  | Type         | Admin |
| --------------- | --------------------- | ------------ | ----- |
| `admin_user`    | System Admin          | Student      | Yes   |
| `laksh_jain`    | Laksh Jain            | Student      | No    |
| `parthiv_p`     | Parthiv Patel         | Student      | No    |
| `ridham_p`      | Ridham Patel          | Student      | No    |
| `shriniket_b`   | Shriniket Behera      | Student      | No    |
| `rudra_s`       | Rudra Singh           | Student      | No    |
| `prof_yogesh`   | Dr. Yogesh K. Meena   | Professor    | No    |
| `prof_anirban`  | Dr. Anirban Dasgupta  | Professor    | No    |
| `alumni_rahul`  | Rahul Sharma          | Alumni       | No    |
| `alumni_priya`  | Priya Verma           | Alumni       | No    |
| `techclub`      | Technical Club IITGN  | Organization | No    |

You can also log in with email instead of username (e.g., `laksh.jain@iitgn.ac.in`).

---

## Features

### Core
- **Authentication** — Register with @iitgn.ac.in email + OTP verification, login with username or email, forgot password with OTP reset
- **Global Feed** — Posts with likes, comments, image uploads, inline edit/delete
- **User Profiles** — Member portfolio with posts, groups, profile claims with community voting
- **Settings** — Update profile, change password, change username (OTP verified)

### Social
- **Groups** — Create public/restricted groups, admin approval for restricted groups, member management (kick, make admin)
- **Polls** — Create polls with multiple options, real-time vote counts
- **Job Board** — Alumni post job listings, students send referral requests

### Academic
- **Attendance Tracking** — Class and mess attendance records, monthly breakdowns, streaks, leaderboard

### Admin
- **Admin Dashboard** — System statistics, manage all members and groups
- **RBAC** — Admin-only endpoints protected by `admin_required` decorator

### Security
- **JWT Authentication** — 24-hour token expiry, `@jwt_required()` on all protected routes
- **Audit Logging** — Dual-channel: file (`logs/audit.log`) + database (`AuditLog` table)
- **Unauthorized API Request Detection** — Custom JWT error handlers (`unauthorized_loader`, `expired_token_loader`, `invalid_token_loader`) catch and log all unauthorized API access attempts (missing token, expired token, tampered token) to `audit.log` with `IsAuthorized = FALSE`
- **RBAC Violation Logging** — Non-admin users attempting admin endpoints are logged as `FORBIDDEN_ACCESS` in `audit.log`
- **Direct DB Modification Detection** — 63 MySQL triggers (INSERT/UPDATE/DELETE on all 21 tables) detect operations that bypass the API. API calls set `@app_username` session variable; direct SQL access leaves it NULL, flagging as `DIRECT_DB_ACCESS` with `IsAuthorized = FALSE` in the AuditLog table
- **Password Security** — bcrypt hashing with salt

---

## Running Benchmarks

To run the performance benchmarking (before vs after indexing):

```bash
cd app/backend
python benchmark.py
```

This will:
1. Drop custom indexes
2. Benchmark 10 queries (100 runs each) without indexes
3. Apply all indexes from `sql/indexes.sql`
4. Re-benchmark the same queries
5. Generate comparison charts in `app/backend/benchmarks/`
6. Save results to `app/backend/benchmark_results.json`

View the full optimization report in `report.ipynb` (Jupyter Notebook).

---

## API Endpoints

| Method | Endpoint                         | Description                    | Auth     |
| ------ | -------------------------------- | ------------------------------ | -------- |
| POST   | `/api/auth/login`                | Login (username or email)      | Public   |
| POST   | `/api/auth/register`             | Register new account           | Public   |
| POST   | `/api/auth/send-otp`             | Send OTP to email              | Public   |
| POST   | `/api/auth/verify-otp`           | Verify OTP code                | Public   |
| POST   | `/api/auth/forgot-password`      | Request password reset OTP     | Public   |
| POST   | `/api/auth/reset-password`       | Reset password with OTP        | Public   |
| GET    | `/api/auth/isAuth`               | Check token validity           | JWT      |
| GET    | `/api/posts`                     | Get feed (global or groups)    | JWT      |
| POST   | `/api/posts`                     | Create post                    | JWT      |
| PUT    | `/api/posts/:id`                 | Update post (author only)      | JWT      |
| DELETE | `/api/posts/:id`                 | Delete post (author/admin)     | JWT      |
| POST   | `/api/posts/:id/like`            | Toggle like                    | JWT      |
| GET    | `/api/posts/:id/comments`        | Get comments                   | JWT      |
| POST   | `/api/posts/:id/comments`        | Add comment                    | JWT      |
| GET    | `/api/groups/`                   | List all groups                | JWT      |
| POST   | `/api/groups/`                   | Create group                   | JWT      |
| PUT    | `/api/groups/:id`                | Update group (admin only)      | JWT      |
| DELETE | `/api/groups/:id`                | Delete group (admin only)      | JWT      |
| POST   | `/api/groups/:id/join`           | Join group                     | JWT      |
| POST   | `/api/groups/:id/leave`          | Leave group                    | JWT      |
| GET    | `/api/groups/:id/pending`        | Pending requests (group admin) | JWT      |
| POST   | `/api/groups/:id/approve/:mid`   | Approve member (group admin)   | JWT      |
| POST   | `/api/groups/:id/reject/:mid`    | Reject member (group admin)    | JWT      |
| POST   | `/api/groups/:id/kick/:mid`      | Kick member (group admin)      | JWT      |
| GET    | `/api/jobs`                      | List job postings              | JWT      |
| POST   | `/api/jobs`                      | Post job (alumni only)         | JWT      |
| GET    | `/api/polls/`                    | List polls                     | JWT      |
| POST   | `/api/polls/`                    | Create poll                    | JWT      |
| POST   | `/api/polls/:id/vote`            | Vote on poll                   | JWT      |
| GET    | `/api/attendance/class`          | Class attendance records       | JWT      |
| GET    | `/api/attendance/mess`           | Mess attendance records        | JWT      |
| GET    | `/api/attendance/streaks`        | Attendance streaks             | JWT      |
| GET    | `/api/profile/:id`               | Get user profile               | JWT      |
| GET    | `/api/members/`                  | Search/filter members          | JWT      |
| PUT    | `/api/settings/profile`          | Update profile                 | JWT      |
| PUT    | `/api/settings/password`         | Change password                | JWT      |
| PUT    | `/api/settings/change-username`  | Change username (OTP required) | JWT      |
| DELETE | `/api/settings/account`          | Delete account                 | JWT      |
| GET    | `/api/admin/stats`               | System statistics              | Admin    |
| GET    | `/api/admin/members`             | List all members               | Admin    |
| DELETE | `/api/admin/members/:id`         | Delete member                  | Admin    |
| DELETE | `/api/admin/groups/:id`          | Delete group                   | Admin    |

---

## Database Schema

22 tables organized into core and feature modules. Full schema in `sql/schema.sql`.

**Core:** Member, Student, Professor, Alumni, Organization
**Content:** Post, Comment, PostLike, Poll, PollOption, PollVote
**Groups:** CampusGroup, GroupMembership
**Academic:** Course, Enrollment, ClassAttendance, MessAttendance
**Jobs:** JobPost, ReferralRequest
**Profile:** ProfileClaimQuestion, ProfileClaimVote
**Security:** AuditLog

---

## Security & Audit Logging

IITGN Connect uses a two-layer security logging system to detect unauthorized access:

### Layer 1: Unauthorized API Request Detection (`audit.log`)

All failed authentication attempts are logged to `logs/audit.log`:

```
# Missing JWT token
[USER:UNAUTHORIZED] [ACTION:UNAUTHORIZED_ACCESS] — Missing/invalid JWT on GET /api/posts

# Expired JWT token
[USER:EXPIRED_TOKEN] [ACTION:UNAUTHORIZED_ACCESS] — Expired JWT (user_id=1) on GET /api/posts

# Tampered/fake JWT token
[USER:INVALID_TOKEN] [ACTION:UNAUTHORIZED_ACCESS] — Invalid/tampered JWT on GET /api/posts

# Non-admin user accessing admin endpoint
[USER:laksh_jain] [ACTION:FORBIDDEN_ACCESS] — Non-admin user 'laksh_jain' attempted GET /api/admin/stats
```

To view unauthorized API attempts:
```bash
# Show all unauthorized access attempts
grep -E "UNAUTHORIZED|FORBIDDEN|INVALID_TOKEN|EXPIRED_TOKEN" logs/audit.log
```

### Layer 2: Direct DB Modification Detection (AuditLog table)

63 MySQL triggers (INSERT/UPDATE/DELETE on all 21 tables) detect operations that bypass the API:

```sql
-- API-based operation (authorized):
-- @app_username is set by db.py before every query
-- Trigger logs: IsAuthorized = TRUE, Username = 'laksh_jain'

-- Direct SQL access (unauthorized):
-- @app_username is NULL (not set by any API call)
-- Trigger logs: IsAuthorized = FALSE, Username = 'DIRECT_DB_ACCESS'

-- To find all unauthorized direct DB modifications:
SELECT * FROM AuditLog WHERE IsAuthorized = FALSE;
```

To test unauthorized DB detection:
```sql
-- Run this directly in MySQL CLI (bypasses the API)
UPDATE Post SET Content = 'Hacked!' WHERE PostID = 1;

-- Check the AuditLog — it will be flagged as unauthorized
SELECT * FROM AuditLog WHERE IsAuthorized = FALSE AND Action = 'UPDATE_POST';
```

---

## Troubleshooting

| Problem | Solution |
| ------- | -------- |
| `ModuleNotFoundError` | Make sure venv is activated: `source venv/bin/activate` |
| `Access denied for user 'root'` | Update MySQL credentials in `app/backend/.env` |
| `Can't connect to MySQL server` | Start MySQL: `brew services start mysql` or `sudo systemctl start mysql` |
| `Port 5001 already in use` | Kill existing process: `lsof -ti :5001 \| xargs kill -9` |
| `Port 5173 already in use` | Kill existing process: `lsof -ti :5173 \| xargs kill -9` |
| OTP email not received | Check SMTP credentials in `.env`, ensure Gmail App Password is correct |
| `seed.py` fails | Ensure MySQL is running and credentials are correct |

---

## Team

- Parthiv Patel
- Shriniket Behera
- Ridham Patel

**Course:** CS 432 — Databases (Semester II, 2025-2026)
**Institute:** Indian Institute of Technology, Gandhinagar

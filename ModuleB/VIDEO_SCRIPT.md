# IITGN Connect - Video Demo Script (3-5 minutes)
## Narrators: Parthiv, Shriniket, Ridham

---

## INTRO (0:00 - 0:15) — Parthiv

**[Screen: Browser on Login page]**

> "Hi, this is our CS432 Databases Assignment 2 Module B submission — IITGN Connect, a college social media platform. I'm Parthiv, and along with Shriniket and Ridham, we'll walk you through our UI, API functionality, RBAC enforcement, and security logging."

---

## PART 1: UI & API Functionality (0:15 - 2:00) — Parthiv

### 1a. Registration with OTP (0:15 - 0:35)

**[Screen: Click "Register" on login page]**

> "Let's start with registration. Our system requires an @iitgn.ac.in email. I'll enter a name, username, and email."

**[Screen: Type in details, click "Send OTP"]**

> "We use Gmail SMTP to send a 6-digit OTP for email verification. Once verified, bcrypt hashes the password before storing it in MySQL."

**[Screen: Enter OTP, complete registration]**

> "Notice the warning — email cannot be changed after registration, which is an intentional security design choice."

### 1b. Login & Feed — CRUD on Posts (0:35 - 1:10)

**[Screen: Login as `laksh_jain` / `password123`]**

> "Now logging in as Laksh. You can use either username or email to log in. The backend issues a JWT token valid for 24 hours."

**[Screen: Show global feed with posts]**

> "This is our global feed — it fetches posts with author info, like counts, and comment counts using JOINs and correlated subqueries. Group-only posts are filtered out here."

**[Screen: Create a new post — type content, optionally upload image]**

> "Let me create a post — this calls POST /api/posts. I can also attach an image."

**[Screen: Click 3-dot menu on own post → Edit → Save]**

> "I can edit my own posts via the 3-dot menu — this calls PUT /api/posts/:id."

**[Screen: Click 3-dot menu → Delete → Confirm]**

> "And delete it — DELETE /api/posts/:id. Only the post author or a system admin can do this."

**[Screen: Like a post, add a comment]**

> "I can also like posts and add comments — each is a separate API call with JWT authentication."

### 1c. Member Portfolio / Profile (1:10 - 1:30)

**[Screen: Click on own profile from sidebar]**

> "The Member Portfolio shows all profile details — name, email, member type, contact number, address with a privacy toggle, and recent posts."

**[Screen: Show profile claims section]**

> "We also have Profile Claims — a Q&A verification feature where other users can vote to verify your claims."

**[Screen: Go to Settings page]**

> "In Settings, users can update their name, contact, address, change their username with OTP verification, or change their password. Email is intentionally locked and cannot be changed."

### 1d. Groups, Jobs, Polls, Attendance (1:30 - 2:00)

**[Screen: Navigate to Groups page]**

> "Users can browse, create, and join groups. Groups can be public or restricted — restricted groups require admin approval."

**[Screen: Open a group → show posts inside]**

> "Each group has its own feed — these posts only appear here, not in the global feed."

**[Screen: Quickly show Jobs page]**

> "Alumni users can post job listings and manage referral requests from students."

**[Screen: Quickly show Polls page]**

> "The polling system lets anyone create polls and vote — results update in real time."

**[Screen: Quickly show Attendance page]**

> "Students can track class and mess attendance with streaks, breakdowns, and a leaderboard."

---

## PART 2: RBAC Enforcement (2:00 - 3:00) — Shriniket

### 2a. Admin Login & Dashboard (2:00 - 2:30)

**[Screen: Logout → Login as `admin_user` / `password123`]**

> "Now I'll demonstrate Role-Based Access Control. I'm logging in as our System Admin account."

**[Screen: Show Admin Dashboard with stats]**

> "The Admin Dashboard shows system-wide statistics — total members, posts, groups, polls, comments, and jobs. This page is protected by an `admin_required` decorator that checks the `IsAdmin` flag on the Member table."

**[Screen: Show Members management tab — list of all members]**

> "As admin, I can view all members, update their details, or delete accounts. Let me delete a test member to demonstrate."

**[Screen: Delete a member → show success]**

> "The deletion cascades — removing the member also removes their posts, comments, group memberships, and all related data through ON DELETE CASCADE foreign keys."

**[Screen: Show Groups management — delete a group]**

> "Similarly, I can delete any group. As admin, I can also delete anyone's post from the feed — not just my own."

### 2b. Regular User — Restricted Access (2:30 - 3:00)

**[Screen: Logout → Login as `ridham_p` / `password123`]**

> "Now logging in as Ridham, a regular user. Notice there's no Admin option in the sidebar."

**[Screen: Try navigating to /admin directly in URL bar]**

> "Even if I manually type /admin in the URL, the backend returns a 403 Forbidden. The `admin_required` decorator checks `IsAdmin` from the database — it's not just a frontend check."

**[Screen: Show that Ridham can only edit/delete own posts, not others']**

> "As a regular user, I can only see the 3-dot menu on my own posts. I cannot edit or delete other users' posts. The backend also enforces this — even if someone crafts a direct API call, the AuthorID check prevents unauthorized modifications."

**[Screen: Show Members page — read-only view]**

> "I can browse members and view profiles, but I have no admin controls. This demonstrates our two-tier RBAC — Admin has full CRUD access while regular users have ownership-scoped permissions."

---

## PART 3: Security Logging (3:00 - 3:50) — Ridham

### 3a. Audit Log File (3:00 - 3:20)

**[Screen: Open terminal, run `cat logs/audit.log | tail -20`]**

> "Our security logging has two channels. First, the file-based audit log. Every data-modifying API call — POST, PUT, DELETE — is logged with timestamp, username, action type, endpoint, IP address, and operation details."

**[Screen: Highlight a few log lines]**

> "For example, here you can see the login event, the post creation, the delete operation we just performed as admin — all timestamped and attributed to the correct user."

### 3b. Database Audit Log Table (3:20 - 3:40)

**[Screen: Open MySQL terminal or any SQL client, run `SELECT * FROM AuditLog ORDER BY Timestamp DESC LIMIT 10;`]**

> "Second channel — the AuditLog database table. Same information stored in MySQL for queryable analysis. Notice the IsAuthorized column — all API operations are marked TRUE."

**[Screen: Run a direct SQL modification to trigger the unauthorized access detection]**

> "Now watch this — if someone tries to modify data directly through SQL, bypassing the API..."

**[Screen: Run `UPDATE Member SET Name='Hacked' WHERE MemberID=3;` directly in MySQL]**

> "...our MySQL triggers detect this. The trigger checks for the absence of our session variables that only the Flask API sets. It logs this as IsAuthorized = FALSE."

**[Screen: Run `SELECT * FROM AuditLog WHERE IsAuthorized = FALSE;` — show the flagged entry]**

> "Here it is — the unauthorized modification is flagged. This is how we detect and log direct database tampering versus legitimate API operations."

### 3c. Wrap-up (3:40 - 3:50)

**[Screen: Show the report.ipynb briefly]**

> "All our benchmarking results, EXPLAIN plan analysis, and indexing strategy are documented in our optimization report. Thank you for watching."

---

## QUICK REFERENCE — Login Credentials

| User | Username | Password | Role |
|------|----------|----------|------|
| Admin | `admin_user` | `password123` | Admin (IsAdmin=TRUE) |
| Student | `laksh_jain` | `password123` | Regular User |
| Student | `ridham_p` | `password123` | Regular User |
| Alumni | `alumni_rahul` | `password123` | Regular User (can post jobs) |

## CHECKLIST — Rubric Coverage

- [x] **UI & API Functionality (20 marks)**: Registration, login, feed, CRUD on posts/comments/likes, profile, groups, jobs, polls, attendance
- [x] **RBAC Enforcement (10 marks)**: Admin dashboard demo, regular user restrictions, 403 on unauthorized access, ownership checks
- [x] **Security Logging (10 marks)**: File-based audit.log, AuditLog DB table, unauthorized modification detection via MySQL triggers
- [x] **Database Optimization (10 marks)**: 26 indexes across 13 tables, benchmark.py with before/after measurements
- [x] **Optimization Report (10 marks)**: report.ipynb with EXPLAIN plans, benchmark charts, documentation
- [x] **Video with Audio (10 marks)**: Clear narration by 3 team members, covers all required topics

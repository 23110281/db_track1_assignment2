# IITGN Connect — Video Demo Script (3-5 minutes)

**Narrators:** Parthiv, Shriniket, Ridham
**Format:** Screen recording with voice-over

---

## INTRO (Parthiv) — 15 seconds

> "Hi, we are Parthiv, Shriniket, and Ridham. This is IITGN Connect — a college social media platform built with React, Flask, and MySQL for our CS 432 Databases assignment. Let me walk you through our implementation."

**Screen:** Show the login page with the IITGN Connect logo.

---

## SECTION 1: UI & API Functionality (Ridham) — 90 seconds

### 1a. Authentication (20s)

> "Our platform supports authentication with email OTP verification. Users can register only with an @iitgn.ac.in email. On registration, an OTP is sent via Gmail SMTP to verify the email."

**Screen:** Show the Registration page. Type in an email, click "Send OTP". Show the OTP input field.

> "Users can login with either their username or email. We also have a forgot password flow that sends an OTP to reset the password."

**Screen:** Show Login page — point out "Username or Email" label and "Forgot password?" link.

### 1b. Member Portfolio / Profile (20s)

> "Each member has a profile page showing their details, groups they belong to, and recent posts. We support four member types — Student, Professor, Alumni, and Organization — each with specific attributes."

**Screen:** Navigate to a profile page (e.g., Laksh Jain). Show the member info, groups section, and recent posts.

> "Profile also has a claims section where other users can make claims about you and the community votes on them."

### 1c. CRUD Operations on Posts (25s)

> "On the global feed, users can create posts with text and images. You can like posts, and comment on them."

**Screen:** Create a new post with some text. Show it appear in the feed. Like it. Open comments, type a comment, submit.

> "Users can edit or delete their own posts using the three-dot menu."

**Screen:** Click the 3-dot menu on your own post. Click Edit, change text, save. Then show delete option.

### 1d. Groups & Search (25s)

> "Users can create groups — either public or restricted. Restricted groups require admin approval to join."

**Screen:** Show the Groups page. Click "Create Group". Fill in name, description, toggle "Restricted". Create it.

> "Group admins can approve or reject join requests, kick members, and promote members to admin. Posts within groups show clickable group badges that navigate directly to the group page. The navbar search bar lets you quickly search for members across the platform."

**Screen:** Show a group post with a clickable group badge. Then type a name in the navbar search bar, press Enter, show results on the Members page.

---

## SECTION 2: RBAC Enforcement (Shriniket) — 75 seconds

### 2a. Admin Login & Dashboard (25s)

> "Now let me demonstrate our Role-Based Access Control. I'll first login as the admin user."

**Screen:** Login as `admin_user` / `password123`.

> "As an admin, I have access to the Admin Dashboard which shows system statistics — total members, posts, groups, polls. I can manage all members and groups from here — edit roles or delete members. Notice the admin cannot delete their own account, and is shown with an 'Admin' badge instead of 'Student'."

**Screen:** Navigate to Admin Dashboard. Show stats. Show member list with Admin badge. Point out the missing delete button on admin's own row.

### 2b. Admin SQL Console (10s)

> "Admins also have access to the SQL Query Console — a terminal-themed interface where they can run raw SQL queries directly from the browser for advanced debugging and management."

**Screen:** Navigate to SQL Console. Run a simple query like `SELECT COUNT(*) FROM Post`. Show the results.

### 2c. Role-Based Feature Visibility (25s)

> "Different member types see different features. As admin, on the Jobs page I can see all postings and delete any job, but I don't see the Apply button, Request Referral button, or My Referrals tab — those are for students and alumni only. On the Attendance page, admin only sees the leaderboard, not individual attendance records."

**Screen:** Show Jobs page as admin — point out the 3-dot menu with Delete on each job, and the absence of Apply/Referral buttons and My Referrals tab. Then show Attendance page — only the leaderboard section is visible.

> "Similarly, Professors and Organizations don't see the Jobs or Attendance sections in the sidebar at all. Alumni don't see Attendance Streaks either."

### 2d. Regular User — Restricted Access (15s)

> "Now I'll logout and login as a regular student — laksh_jain."

**Screen:** Logout. Login as `laksh_jain` / `password123`.

> "Notice that the Admin Dashboard and SQL Console options are not visible in the sidebar. On the Jobs page, the student sees Apply and Request Referral buttons, and the My Referrals tab to track their referral requests."

**Screen:** Show the sidebar — no Admin/SQL Console options. Show Jobs page with Apply, Request Referral (click it to show "Referral Sent!" feedback), and My Referrals tab.

---

## SECTION 3: Security Logging (Parthiv) — 60 seconds

### 3a. Audit Log File — Authorized Operations (20s)

> "Every data-modifying API operation is logged to our audit.log file with timestamps, usernames, actions, endpoints, and IP addresses."

**Screen:** Open terminal. Run:
```bash
cat logs/audit.log
```

> "Here you can see successful login attempts, post creations, likes, comments — all with the actual authenticated username."

**Screen:** Highlight a few log lines showing `[USER:laksh_jain] [ACTION:POST]` etc.

### 3b. Unauthorized API Requests (25s)

> "Now let me show how we detect unauthorized API access. We use Flask-JWT-Extended's error handler hooks — `unauthorized_loader` for missing tokens, `expired_token_loader` for expired tokens, and `invalid_token_loader` for tampered or fake tokens. Each of these handlers intercepts the failed request, logs it to both audit.log and the AuditLog database table with `IsAuthorized = FALSE`, and returns a 401 response."

> "For RBAC violations, we have an `admin_required` decorator that checks the `IsAdmin` flag in the Member table. If a non-admin user tries to access an admin endpoint, it logs the attempt as `FORBIDDEN_ACCESS` and returns a 403."

> "Let me demonstrate — I'll make a request without any JWT token."

**Screen:** Run in terminal:
```bash
curl http://localhost:5001/api/posts
```

Show the 401 response, then:
```bash
grep "UNAUTHORIZED" logs/audit.log
```

> "The log clearly shows UNAUTHORIZED ACCESS with the endpoint, IP address, and reason. Similarly, expired and tampered tokens are all caught and logged separately."

**Screen:** Highlight the `UNAUTHORIZED_ACCESS` and `FORBIDDEN_ACCESS` entries in the log.

### 3c. Direct Database Modification Detection via Triggers (30s)

> "Finally, we have 63 MySQL triggers across all 21 tables that detect direct database modifications — someone bypassing our API entirely and running SQL directly. Here's how it works:"

> "Every table has three triggers — one each for INSERT, UPDATE, and DELETE. The key mechanism is a MySQL session variable called `@app_username`. Whenever our Flask backend runs a query, it first sets this variable to the authenticated user's username via `SET @app_username = 'laksh_jain'`. The triggers check this variable — if it's set, the operation came through our API and is logged as authorized. If it's NULL, that means someone ran the query directly in MySQL without going through the API, and the trigger logs it as unauthorized with username 'DIRECT_DB_ACCESS'."

**Screen:** Show one of the triggers in seed.py or run:
```sql
SHOW TRIGGERS LIKE 'Post'\G
```
Highlight the `IF @app_username IS NULL` logic in the trigger body.

> "Let me demonstrate. I'll modify a post directly in MySQL CLI — bypassing the API."

**Screen:** Open MySQL CLI:
```sql
mysql -u root -proot iitgn_connect
UPDATE Post SET Content = 'Hacked post!' WHERE PostID = 1;
```

Then:
```sql
SELECT Timestamp, Username, Action, Details, IsAuthorized
FROM AuditLog WHERE IsAuthorized = FALSE ORDER BY Timestamp DESC LIMIT 5;
```

> "The trigger caught it — Username is 'DIRECT_DB_ACCESS', Endpoint is 'DIRECT_SQL', and IsAuthorized is FALSE. Compare this with API-based operations which show the real username and IsAuthorized as TRUE. So any direct database modification that bypasses our session-validated API is easily identifiable just by querying `WHERE IsAuthorized = FALSE`."

**Screen:** Show the query result highlighting `DIRECT_DB_ACCESS` with `IsAuthorized = 0`. Then contrast with:
```sql
SELECT Timestamp, Username, Action, IsAuthorized
FROM AuditLog WHERE IsAuthorized = TRUE ORDER BY Timestamp DESC LIMIT 5;
```

---

## CLOSING (Ridham) — 10 seconds

> "That covers our IITGN Connect platform — full CRUD operations, role-based access control with feature-level visibility per member type, and comprehensive security logging at both the API and database level. Thank you!"

**Screen:** Show the IITGN Connect home page.

---

## KEY TIMESTAMPS

| Time | Section | Narrator |
|------|---------|----------|
| 0:00 | Intro | Parthiv |
| 0:15 | Authentication & Registration | Ridham |
| 0:35 | Member Portfolio / Profile | Ridham |
| 0:55 | CRUD on Posts (create, edit, delete, like, comment) | Ridham |
| 1:20 | Groups, Search & Navigation | Ridham |
| 1:45 | RBAC — Admin Login & Dashboard | Shriniket |
| 2:10 | RBAC — SQL Query Console | Shriniket |
| 2:20 | RBAC — Role-Based Feature Visibility | Shriniket |
| 2:45 | RBAC — Regular User Restrictions | Shriniket |
| 3:00 | Audit Log — Authorized Operations | Parthiv |
| 3:20 | Unauthorized API Request Detection — JWT Error Handlers | Parthiv |
| 3:45 | Direct DB Modification Detection — Trigger Implementation | Parthiv |
| 4:15 | Closing | Ridham |

---

## CHECKLIST (Rubric Coverage)

- [x] **UI & API Functionality** (20 marks) — Login, Registration, Member Portfolio, Global Feed, Posts CRUD, Groups, Comments, Likes, Global Search, Job Board with Referrals, Polls, Attendance
- [x] **RBAC Enforcement** (10 marks) — Admin vs Regular User login, Admin Dashboard + SQL Console access, role-based sidebar visibility (Jobs hidden for Prof/Org, Attendance hidden for Alumni/Prof), admin can delete any post/comment/job, feature-level controls (Apply/Referral buttons hidden for admin, attendance details hidden for admin), 403 on unauthorized admin API access, admin_required decorator
- [x] **Security Logging** (10 marks) — audit.log with authorized operations, unauthorized API requests (401), RBAC violations (403), direct DB modifications detected via triggers (IsAuthorized=FALSE)
- [x] **Clear Audio Narration** — Three narrators covering all sections with explanations of implementation details

## TIPS FOR RECORDING

1. **Keep MySQL CLI open** in a terminal tab before recording — saves time
2. **Pre-clear audit.log** before recording so entries are clean: `> logs/audit.log`
3. **Pre-login** as admin_user in one browser and laksh_jain in an incognito window for quick switching
4. **Zoom in** on terminal text so it's readable in the video
5. **Practice once** before recording — aim for 3:30-4:00 minutes
6. Upload to **YouTube (Unlisted)** or **Google Drive** and paste link in `report.ipynb`

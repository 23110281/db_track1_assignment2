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

### 1d. Groups (25s)

> "Users can create groups — either public or restricted. Restricted groups require admin approval to join."

**Screen:** Show the Groups page. Click "Create Group". Fill in name, description, toggle "Restricted". Create it.

> "Group admins can approve or reject join requests, kick members, and promote members to admin. Posts within groups only appear in the My Groups feed tab, not the global feed."

**Screen:** Show a restricted group with pending requests. Approve one. Show the 3-dot menu on a member (Make Admin / Kick).

---

## SECTION 2: RBAC Enforcement (Shriniket) — 60 seconds

### 2a. Admin Login (25s)

> "Now let me demonstrate our Role-Based Access Control. I'll first login as the admin user."

**Screen:** Login as `admin_user` / `password123`.

> "As an admin, I have access to the Admin Dashboard which shows system statistics — total members, posts, groups, comments. I can also manage all members and groups from here — edit roles, toggle admin status, or delete members."

**Screen:** Navigate to Admin Dashboard. Show stats. Show member list. Toggle a user's admin status or change their role.

### 2b. Regular User — Restricted Access (20s)

> "Now I'll logout and login as a regular user — laksh_jain."

**Screen:** Logout. Login as `laksh_jain` / `password123`.

> "Notice that the Admin Dashboard option is not visible in the sidebar for regular users. The admin route is completely hidden."

**Screen:** Show the sidebar — no Admin option visible.

### 2c. API-Level RBAC (15s)

> "Even if someone tries to access the admin API directly — for example by calling /api/admin/stats — our backend rejects it with a 403 Forbidden error and logs it as a FORBIDDEN_ACCESS attempt."

**Screen:** Open browser DevTools (Network tab). Try navigating to admin URL directly or use curl:
```
curl http://localhost:5001/api/admin/stats -H "Authorization: Bearer <laksh_token>"
```
Show the 403 response.

> "This is enforced by the admin_required decorator which checks the IsAdmin flag in the database before allowing access."

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

### 3b. Unauthorized API Requests (20s)

> "Now let me show how we detect unauthorized API access. I'll make a request without any JWT token."

**Screen:** Run in terminal:
```bash
curl http://localhost:5001/api/posts
```

Show the 401 response, then:
```bash
grep "UNAUTHORIZED" logs/audit.log
```

> "The log clearly shows UNAUTHORIZED ACCESS — missing JWT. Similarly, expired tokens and tampered tokens are all caught and logged. And as we saw, non-admin users trying admin endpoints are logged as FORBIDDEN ACCESS."

**Screen:** Highlight the `UNAUTHORIZED_ACCESS` and `FORBIDDEN_ACCESS` entries in the log.

### 3c. Direct Database Modification Detection (20s)

> "Finally, we have 63 MySQL triggers across all 21 tables that detect direct database modifications — someone bypassing our API entirely and running SQL directly."

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

> "The trigger caught it — Username is 'DIRECT_DB_ACCESS', Endpoint is 'DIRECT_SQL', and IsAuthorized is FALSE. Compare this with API-based operations which show the real username and IsAuthorized as TRUE. This way, any unauthorized database modifications are easily identifiable."

**Screen:** Show the query result highlighting `DIRECT_DB_ACCESS` with `IsAuthorized = 0`.

---

## CLOSING (Ridham) — 10 seconds

> "That covers our IITGN Connect platform — full CRUD operations, role-based access control, and comprehensive security logging at both the API and database level. Thank you!"

**Screen:** Show the IITGN Connect home page.

---

## KEY TIMESTAMPS

| Time | Section | Narrator |
|------|---------|----------|
| 0:00 | Intro | Parthiv |
| 0:15 | Authentication & Registration | Ridham |
| 0:35 | Member Portfolio / Profile | Ridham |
| 0:55 | CRUD on Posts (create, edit, delete, like, comment) | Ridham |
| 1:20 | Groups (create, restricted, approve, kick) | Ridham |
| 1:45 | RBAC — Admin Login & Dashboard | Shriniket |
| 2:10 | RBAC — Regular User Restrictions | Shriniket |
| 2:30 | RBAC — API-Level 403 Enforcement | Shriniket |
| 2:45 | Audit Log — Authorized Operations | Parthiv |
| 3:05 | Unauthorized API Request Detection | Parthiv |
| 3:25 | Direct DB Modification Detection (Triggers) | Parthiv |
| 3:45 | Closing | Ridham |

---

## CHECKLIST (Rubric Coverage)

- [x] **UI & API Functionality** (20 marks) — Login, Registration, Member Portfolio, Global Feed, Posts CRUD, Groups, Comments, Likes
- [x] **RBAC Enforcement** (10 marks) — Admin vs Regular User login, admin dashboard access, 403 on unauthorized admin access, admin_required decorator
- [x] **Security Logging** (10 marks) — audit.log with authorized operations, unauthorized API requests (401), RBAC violations (403), direct DB modifications detected via triggers (IsAuthorized=FALSE)
- [x] **Clear Audio Narration** — Three narrators covering all sections with explanations of implementation details

## TIPS FOR RECORDING

1. **Keep MySQL CLI open** in a terminal tab before recording — saves time
2. **Pre-clear audit.log** before recording so entries are clean: `> logs/audit.log`
3. **Pre-login** as admin_user in one browser and laksh_jain in an incognito window for quick switching
4. **Zoom in** on terminal text so it's readable in the video
5. **Practice once** before recording — aim for 3:30-4:00 minutes
6. Upload to **YouTube (Unlisted)** or **Google Drive** and paste link in `report.ipynb`

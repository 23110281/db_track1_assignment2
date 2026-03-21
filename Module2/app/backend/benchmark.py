"""
benchmark.py  --  SQL Index Performance Benchmarking for IITGN Connect
CS432 Databases Module B

Measures query execution times BEFORE and AFTER applying indexes defined in
sql/indexes.sql, runs EXPLAIN analysis, and generates comparison charts.

Usage:  python benchmark.py
Outputs:
  - Console table with timing results
  - benchmark_results.json
  - benchmarks/  directory with PNG bar charts
"""

import json
import os
import time
import textwrap

import mysql.connector
import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# Database config
# ---------------------------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "iitgn_connect",
}

NUM_RUNS = 100  # iterations per query for timing

# ---------------------------------------------------------------------------
# Benchmark queries  --  representative queries taken from the API routes
# ---------------------------------------------------------------------------
QUERIES = [
    {
        "name": "Global Post Feed",
        "description": "Fetch all posts with author info, like/comment counts, ordered by date",
        "sql": textwrap.dedent("""\
            SELECT p.*, m.Username, m.Name, m.MemberType, m.AvatarColor,
                   g.Name AS GroupName,
                   (SELECT COUNT(*) FROM PostLike WHERE PostID = p.PostID) AS likes,
                   (SELECT COUNT(*) FROM Comment WHERE PostID = p.PostID) AS commentCount
            FROM Post p
            JOIN Member m ON p.AuthorID = m.MemberID
            LEFT JOIN CampusGroup g ON p.GroupID = g.GroupID
            ORDER BY p.CreatedAt DESC
        """),
        "params": None,
    },
    {
        "name": "Group Posts",
        "description": "Posts for a specific group with counts, ordered by date",
        "sql": textwrap.dedent("""\
            SELECT p.*, m.Username, m.Name, m.MemberType, m.AvatarColor,
                   (SELECT COUNT(*) FROM PostLike WHERE PostID = p.PostID) AS likes,
                   (SELECT COUNT(*) FROM Comment WHERE PostID = p.PostID) AS commentCount
            FROM Post p
            JOIN Member m ON p.AuthorID = m.MemberID
            WHERE p.GroupID = 4
            ORDER BY p.CreatedAt DESC
        """),
        "params": None,
    },
    {
        "name": "Post Comments",
        "description": "All comments for a post with author details, ordered chronologically",
        "sql": textwrap.dedent("""\
            SELECT c.*, m.Username, m.Name, m.MemberType, m.AvatarColor
            FROM Comment c
            JOIN Member m ON c.AuthorID = m.MemberID
            WHERE c.PostID = 1
            ORDER BY c.CreatedAt ASC
        """),
        "params": None,
    },
    {
        "name": "User Profile Posts",
        "description": "Recent posts by a member for profile page",
        "sql": textwrap.dedent("""\
            SELECT p.*,
                   (SELECT COUNT(*) FROM PostLike WHERE PostID = p.PostID) AS likes,
                   (SELECT COUNT(*) FROM Comment WHERE PostID = p.PostID) AS commentCount,
                   g.Name AS GroupName
            FROM Post p
            LEFT JOIN CampusGroup g ON p.GroupID = g.GroupID
            WHERE p.AuthorID = 1
            ORDER BY p.CreatedAt DESC
            LIMIT 10
        """),
        "params": None,
    },
    {
        "name": "Class Attendance",
        "description": "Monthly class attendance with course info for a student",
        "sql": textwrap.dedent("""\
            SELECT ca.AttendanceID, ca.CourseID, ca.RecordDate, ca.Status,
                   c.CourseCode, c.CourseName
            FROM ClassAttendance ca
            JOIN Course c ON ca.CourseID = c.CourseID
            WHERE ca.StudentID = 1
              AND MONTH(ca.RecordDate) = 3
              AND YEAR(ca.RecordDate) = 2026
            ORDER BY ca.RecordDate
        """),
        "params": None,
    },
    {
        "name": "Mess Attendance",
        "description": "Monthly mess attendance records for a student",
        "sql": textwrap.dedent("""\
            SELECT * FROM MessAttendance
            WHERE StudentID = 1
              AND MONTH(RecordDate) = 3
              AND YEAR(RecordDate) = 2026
            ORDER BY RecordDate, FIELD(MealType, 'Breakfast', 'Lunch', 'Dinner')
        """),
        "params": None,
    },
    {
        "name": "Job Listings",
        "description": "All job posts with alumni info, ordered by posting date",
        "sql": textwrap.dedent("""\
            SELECT j.*, m.Name AS AlumniName, m.AvatarColor,
                   a.CurrentOrganization
            FROM JobPost j
            JOIN Member m ON j.AlumniID = m.MemberID
            JOIN Alumni a ON j.AlumniID = a.MemberID
            ORDER BY j.PostedAt DESC
        """),
        "params": None,
    },
    {
        "name": "Referral Requests (Alumni)",
        "description": "Referral requests received by an alumni, newest first",
        "sql": textwrap.dedent("""\
            SELECT r.*, m.Name AS StudentName
            FROM ReferralRequest r
            JOIN Member m ON r.StudentID = m.MemberID
            WHERE r.TargetAlumniID = 8
            ORDER BY r.RequestedAt DESC
        """),
        "params": None,
    },
    {
        "name": "Polls with Options & Votes",
        "description": "All polls with vote counts per option",
        "sql": textwrap.dedent("""\
            SELECT p.*, m.Name AS CreatorName, m.AvatarColor
            FROM Poll p
            JOIN Member m ON p.CreatorID = m.MemberID
            ORDER BY p.CreatedAt DESC
        """),
        "params": None,
    },
    {
        "name": "Member Search by Type",
        "description": "Filter members by type and order by name",
        "sql": textwrap.dedent("""\
            SELECT MemberID, Username, Name, Email, MemberType, ContactNumber,
                   CreatedAt, AvatarColor
            FROM Member
            WHERE MemberType = 'Student'
            ORDER BY Name
        """),
        "params": None,
    },
]


# ---------------------------------------------------------------------------
# Index definitions  --  parsed from sql/indexes.sql
# ---------------------------------------------------------------------------
INDEX_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "sql", "indexes.sql")


def _parse_index_statements(filepath):
    """Return a list of CREATE INDEX statements from the SQL file."""
    with open(filepath, "r") as f:
        content = f.read()
    stmts = []
    for line in content.split(";"):
        line = line.strip()
        if line.upper().startswith("CREATE INDEX") or line.upper().startswith("CREATE UNIQUE INDEX"):
            stmts.append(line + ";")
    return stmts


def _extract_index_names(statements):
    """Return list of (index_name, table_name) from CREATE INDEX statements."""
    pairs = []
    for stmt in statements:
        parts = stmt.split()
        idx = parts[2]  # index name
        table = parts[4]  # table name
        pairs.append((idx, table))
    return pairs


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def run_explain(cursor, sql):
    """Run EXPLAIN on a query and return the result rows as list of dicts."""
    cursor.execute("EXPLAIN " + sql)
    columns = [d[0] for d in cursor.description]
    rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]


def measure_time(cursor, sql, n=NUM_RUNS):
    """Execute a query n times and return average time in milliseconds."""
    # Warm-up run
    cursor.execute(sql)
    cursor.fetchall()

    times = []
    for _ in range(n):
        start = time.perf_counter()
        cursor.execute(sql)
        cursor.fetchall()
        end = time.perf_counter()
        times.append((end - start) * 1000)  # ms
    return sum(times) / len(times)


def drop_custom_indexes(cursor, index_pairs):
    """Safely drop all custom indexes (ignoring errors for missing ones)."""
    for idx_name, table_name in index_pairs:
        try:
            cursor.execute(f"DROP INDEX `{idx_name}` ON `{table_name}`")
        except mysql.connector.Error:
            pass  # index does not exist yet


def apply_indexes(cursor, statements):
    """Apply all CREATE INDEX statements, skipping duplicates."""
    for stmt in statements:
        try:
            cursor.execute(stmt)
        except mysql.connector.Error as e:
            if e.errno == 1061:  # Duplicate key name
                pass
            else:
                print(f"  Warning: {e.msg}")


def format_explain(explain_rows):
    """Return a compact string summary of EXPLAIN output."""
    parts = []
    for row in explain_rows:
        table = row.get("table", "?")
        access = row.get("type", "?")
        key = row.get("key", "None")
        rows_est = row.get("rows", "?")
        extra = row.get("Extra", "")
        parts.append(f"{table}: type={access}, key={key}, rows={rows_est}, extra={extra}")
    return " | ".join(parts)


# ---------------------------------------------------------------------------
# Main benchmark
# ---------------------------------------------------------------------------

def main():
    index_stmts = _parse_index_statements(INDEX_FILE)
    index_pairs = _extract_index_names(index_stmts)

    conn = get_connection()
    cursor = conn.cursor()

    # Ensure clean state  --  drop all custom indexes first
    print("Dropping existing custom indexes (if any)...")
    drop_custom_indexes(cursor, index_pairs)
    conn.commit()

    results = []

    print(f"\nBenchmarking {len(QUERIES)} queries  ({NUM_RUNS} runs each)\n")
    print("=" * 100)

    for i, q in enumerate(QUERIES, 1):
        name = q["name"]
        sql = q["sql"]
        print(f"\n[{i}/{len(QUERIES)}] {name}")
        print(f"  {q['description']}")

        # --- BEFORE indexes ---
        explain_before = run_explain(cursor, sql)
        time_before = measure_time(cursor, sql)

        # --- Apply indexes ---
        apply_indexes(cursor, index_stmts)
        conn.commit()

        # --- AFTER indexes ---
        explain_after = run_explain(cursor, sql)
        time_after = measure_time(cursor, sql)

        # --- Drop indexes again for next query's "before" measurement ---
        drop_custom_indexes(cursor, index_pairs)
        conn.commit()

        # --- Compute speedup ---
        if time_after > 0:
            speedup = ((time_before - time_after) / time_before) * 100
        else:
            speedup = 0.0

        result = {
            "name": name,
            "description": q["description"],
            "time_before_ms": round(time_before, 4),
            "time_after_ms": round(time_after, 4),
            "speedup_pct": round(speedup, 2),
            "explain_before": explain_before,
            "explain_after": explain_after,
            "explain_before_summary": format_explain(explain_before),
            "explain_after_summary": format_explain(explain_after),
        }
        results.append(result)

        print(f"  Before: {time_before:.4f} ms  |  After: {time_after:.4f} ms  |  Speedup: {speedup:+.2f}%")
        print(f"  EXPLAIN before: {format_explain(explain_before)}")
        print(f"  EXPLAIN after:  {format_explain(explain_after)}")

    # --- Re-apply indexes so the database keeps them for production ---
    print("\nRe-applying all indexes for production use...")
    apply_indexes(cursor, index_stmts)
    conn.commit()

    cursor.close()
    conn.close()

    # -----------------------------------------------------------------------
    # Console summary table
    # -----------------------------------------------------------------------
    print("\n" + "=" * 100)
    print(f"{'Query':<35} {'Before (ms)':>12} {'After (ms)':>12} {'Speedup':>10}")
    print("-" * 100)
    for r in results:
        print(f"{r['name']:<35} {r['time_before_ms']:>12.4f} {r['time_after_ms']:>12.4f} {r['speedup_pct']:>+9.2f}%")
    print("=" * 100)

    avg_speedup = sum(r["speedup_pct"] for r in results) / len(results) if results else 0
    print(f"Average speedup: {avg_speedup:+.2f}%\n")

    # -----------------------------------------------------------------------
    # Save JSON
    # -----------------------------------------------------------------------
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "benchmark_results.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Results saved to {json_path}")

    # -----------------------------------------------------------------------
    # Generate charts
    # -----------------------------------------------------------------------
    charts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "benchmarks")
    os.makedirs(charts_dir, exist_ok=True)

    names = [r["name"] for r in results]
    before_times = [r["time_before_ms"] for r in results]
    after_times = [r["time_after_ms"] for r in results]
    speedups = [r["speedup_pct"] for r in results]

    # --- Chart 1: Grouped bar chart  (before vs after) ---
    fig, ax = plt.subplots(figsize=(14, 7))
    x = np.arange(len(names))
    width = 0.35

    bars1 = ax.bar(x - width / 2, before_times, width, label="Before Indexing", color="#EF4444", alpha=0.85)
    bars2 = ax.bar(x + width / 2, after_times, width, label="After Indexing", color="#22C55E", alpha=0.85)

    ax.set_xlabel("Query", fontsize=12)
    ax.set_ylabel("Avg Execution Time (ms)", fontsize=12)
    ax.set_title("Query Performance: Before vs After Indexing", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=35, ha="right", fontsize=9)
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)

    # Add value labels on bars
    for bar in bars1:
        h = bar.get_height()
        ax.annotate(f"{h:.3f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=7)
    for bar in bars2:
        h = bar.get_height()
        ax.annotate(f"{h:.3f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=7)

    fig.tight_layout()
    chart1_path = os.path.join(charts_dir, "before_vs_after.png")
    fig.savefig(chart1_path, dpi=150)
    plt.close(fig)
    print(f"Chart saved: {chart1_path}")

    # --- Chart 2: Speedup percentage bar chart ---
    fig2, ax2 = plt.subplots(figsize=(14, 7))
    colors = ["#22C55E" if s >= 0 else "#EF4444" for s in speedups]
    bars3 = ax2.bar(x, speedups, 0.6, color=colors, alpha=0.85)

    ax2.set_xlabel("Query", fontsize=12)
    ax2.set_ylabel("Speedup (%)", fontsize=12)
    ax2.set_title("Index Speedup by Query", fontsize=14, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(names, rotation=35, ha="right", fontsize=9)
    ax2.axhline(y=0, color="black", linewidth=0.5)
    ax2.grid(axis="y", alpha=0.3)

    for bar, val in zip(bars3, speedups):
        h = bar.get_height()
        ax2.annotate(f"{val:+.1f}%", xy=(bar.get_x() + bar.get_width() / 2, h),
                      xytext=(0, 3 if h >= 0 else -12), textcoords="offset points",
                      ha="center", va="bottom" if h >= 0 else "top", fontsize=9, fontweight="bold")

    fig2.tight_layout()
    chart2_path = os.path.join(charts_dir, "speedup_pct.png")
    fig2.savefig(chart2_path, dpi=150)
    plt.close(fig2)
    print(f"Chart saved: {chart2_path}")

    # --- Chart 3: EXPLAIN key usage comparison (horizontal) ---
    fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(16, 7))

    before_keys = []
    after_keys = []
    for r in results:
        bk = set()
        for e in r["explain_before"]:
            if e.get("key"):
                bk.add(e["key"])
        before_keys.append(", ".join(bk) if bk else "None")

        ak = set()
        for e in r["explain_after"]:
            if e.get("key"):
                ak.add(e["key"])
        after_keys.append(", ".join(ak) if ak else "None")

    # Before
    ax3a.set_title("Keys Used BEFORE Indexing", fontsize=12, fontweight="bold")
    ax3a.barh(range(len(names)), [1] * len(names), color="#FCA5A5", alpha=0.5)
    for i, (n, k) in enumerate(zip(names, before_keys)):
        ax3a.text(0.05, i, f"{n}:  {k}", va="center", fontsize=8)
    ax3a.set_yticks([])
    ax3a.set_xticks([])
    ax3a.set_xlim(0, 1)

    # After
    ax3b.set_title("Keys Used AFTER Indexing", fontsize=12, fontweight="bold")
    ax3b.barh(range(len(names)), [1] * len(names), color="#BBF7D0", alpha=0.5)
    for i, (n, k) in enumerate(zip(names, after_keys)):
        ax3b.text(0.05, i, f"{n}:  {k}", va="center", fontsize=8)
    ax3b.set_yticks([])
    ax3b.set_xticks([])
    ax3b.set_xlim(0, 1)

    fig3.suptitle("EXPLAIN Key Usage Comparison", fontsize=14, fontweight="bold")
    fig3.tight_layout()
    chart3_path = os.path.join(charts_dir, "explain_keys.png")
    fig3.savefig(chart3_path, dpi=150)
    plt.close(fig3)
    print(f"Chart saved: {chart3_path}")

    print("\nBenchmark complete.")


if __name__ == "__main__":
    main()

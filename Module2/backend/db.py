import mysql.connector
import config


def get_db():
    return mysql.connector.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DB,
    )


def query_db(sql, args=None, one=False):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, args or ())
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    if one:
        return rows[0] if rows else None
    return rows


def _set_audit_session_vars(cursor):
    """Set MySQL session variables so triggers can identify API-based operations."""
    try:
        from flask import request as flask_request, has_request_context
        from flask_jwt_extended import get_jwt_identity
        if has_request_context():
            username = 'anonymous'
            try:
                uid = get_jwt_identity()
                if uid:
                    cursor.execute("SELECT Username FROM Member WHERE MemberID = %s", (int(uid),))
                    row = cursor.fetchone()
                    if row:
                        username = row[0]
            except Exception:
                pass
            cursor.execute("SET @app_username = %s", (username,))
            cursor.execute("SET @app_endpoint = %s", (flask_request.path,))
            cursor.execute("SET @app_ip = %s", (flask_request.remote_addr or '127.0.0.1',))
    except Exception:
        pass


def execute_db(sql, args=None):
    conn = get_db()
    cursor = conn.cursor()
    _set_audit_session_vars(cursor)
    cursor.execute(sql, args or ())
    conn.commit()
    last_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return last_id

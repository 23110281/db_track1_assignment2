from datetime import timedelta
from flask import Flask, request as flask_request
from flask_cors import CORS
from flask_jwt_extended import JWTManager

import config
from audit import log_action, log_to_db, get_current_username
from routes.auth import auth_bp
from routes.posts import posts_bp
from routes.groups import groups_bp
from routes.jobs import jobs_bp
from routes.polls import polls_bp
from routes.attendance import attendance_bp
from routes.profile import profile_bp
from routes.members import members_bp
from routes.admin import admin_bp
from routes.settings import settings_bp

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=config.JWT_ACCESS_TOKEN_EXPIRES)

CORS(app, origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
JWTManager(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(posts_bp, url_prefix='/api')
app.register_blueprint(groups_bp, url_prefix='/api/groups')
app.register_blueprint(jobs_bp, url_prefix='/api')
app.register_blueprint(polls_bp, url_prefix='/api/polls')
app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
app.register_blueprint(profile_bp, url_prefix='/api')
app.register_blueprint(members_bp, url_prefix='/api/members')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(settings_bp, url_prefix='/api/settings')


# --- Audit logging: log all data-modifying requests ---
@app.after_request
def audit_log_request(response):
    if flask_request.method in ('POST', 'PUT', 'DELETE'):
        username = 'anonymous'
        try:
            username = get_current_username()
        except Exception:
            pass
        status = response.status_code
        details = f"{flask_request.method} {flask_request.path} -> {status}"
        log_action(flask_request.method, details, user=username)
        log_to_db(
            username=username,
            action=flask_request.method,
            endpoint=flask_request.path,
            ip=flask_request.remote_addr or '127.0.0.1',
            details=details,
            is_authorized=True,
        )
    return response


@app.route('/')
def welcome():
    return {'message': 'Welcome to test APIs'}


@app.route('/api/health')
def health():
    return {'status': 'ok'}


if __name__ == '__main__':
    app.run(debug=True, port=5001)

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from db import query_db, execute_db
from audit import log_action

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify(error='Username and password required'), 400

    member = query_db("SELECT * FROM Member WHERE Username = %s", (username,), one=True)
    if not member or not check_password_hash(member['Password'], password):
        return jsonify(error='Invalid credentials'), 401

    # Get subtype details
    subtype = {}
    if member['MemberType'] == 'Student':
        subtype = query_db("SELECT * FROM Student WHERE MemberID = %s", (member['MemberID'],), one=True) or {}
    elif member['MemberType'] == 'Professor':
        subtype = query_db("SELECT * FROM Professor WHERE MemberID = %s", (member['MemberID'],), one=True) or {}
    elif member['MemberType'] == 'Alumni':
        subtype = query_db("SELECT * FROM Alumni WHERE MemberID = %s", (member['MemberID'],), one=True) or {}
    elif member['MemberType'] == 'Organization':
        subtype = query_db("SELECT * FROM Organization WHERE MemberID = %s", (member['MemberID'],), one=True) or {}

    token = create_access_token(identity=str(member['MemberID']))

    user = {
        'MemberID': member['MemberID'],
        'Username': member['Username'],
        'Name': member['Name'],
        'Email': member['Email'],
        'MemberType': member['MemberType'],
        'ContactNumber': member['ContactNumber'],
        'CreatedAt': str(member['CreatedAt']),
        'avatarColor': member['AvatarColor'],
        'isAdmin': bool(member['IsAdmin']),
        'role': 'Admin' if member['IsAdmin'] else 'Regular',
    }

    # Merge subtype fields
    for k, v in subtype.items():
        if k != 'MemberID':
            user[k] = str(v) if hasattr(v, 'isoformat') else v

    log_action('LOGIN', f"User '{username}' logged in successfully", user=username)
    return jsonify(message="Login successful", token=token, session_token=token, user=user)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    member_type = data.get('memberType', '')
    contact = data.get('contactNumber', '')

    if not all([username, name, email, password, member_type]):
        return jsonify(error='All fields are required'), 400

    existing = query_db("SELECT MemberID FROM Member WHERE Username = %s OR Email = %s", (username, email), one=True)
    if existing:
        return jsonify(error='Username or email already exists'), 409

    pw_hash = generate_password_hash(password)
    member_id = execute_db(
        "INSERT INTO Member (Username, Name, Email, Password, MemberType, ContactNumber, CreatedAt, AvatarColor) VALUES (%s,%s,%s,%s,%s,%s, CURDATE(), '#4F46E5')",
        (username, name, email, pw_hash, member_type, contact),
    )

    # Insert subtype row
    if member_type == 'Student':
        execute_db(
            "INSERT INTO Student (MemberID, Programme, Branch, CurrentYear, MessAssignment) VALUES (%s,%s,%s,%s,%s)",
            (member_id, data.get('programme', ''), data.get('branch', ''), data.get('currentYear', 1), data.get('messAssignment', '')),
        )
    elif member_type == 'Professor':
        execute_db(
            "INSERT INTO Professor (MemberID, Designation, Department, JoiningDate) VALUES (%s,%s,%s, CURDATE())",
            (member_id, data.get('designation', ''), data.get('department', '')),
        )
    elif member_type == 'Alumni':
        execute_db(
            "INSERT INTO Alumni (MemberID, CurrentOrganization, GraduationYear, Verified) VALUES (%s,%s,%s, FALSE)",
            (member_id, data.get('currentOrganization', ''), data.get('graduationYear', 2024)),
        )
    elif member_type == 'Organization':
        execute_db(
            "INSERT INTO Organization (MemberID, OrgType, FoundationDate, ContactEmail) VALUES (%s,%s, CURDATE(),%s)",
            (member_id, data.get('orgType', ''), email),
        )

    log_action('REGISTER', f"New {member_type} registered: '{username}' (ID: {member_id})", user=username)
    return jsonify(message='Registration successful', memberId=member_id), 201


@auth_bp.route('/isAuth', methods=['GET'])
@jwt_required()
def is_authenticated():
    try:
        member_id = get_jwt_identity()
        jwt_data = get_jwt()

        member = query_db("SELECT Username, IsAdmin FROM Member WHERE MemberID = %s", (member_id,), one=True)
        if not member:
            return jsonify(error="No session found"), 401

        role = "Admin" if member['IsAdmin'] else "Regular"
        expiry = datetime.fromtimestamp(jwt_data['exp']).isoformat()

        return jsonify(
            message="User is authenticated",
            username=member['Username'],
            role=role,
            expiry=expiry
        ), 200
    except Exception as e:
        return jsonify(error="Invalid token", details=str(e)), 401

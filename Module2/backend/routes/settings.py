from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from db import query_db, execute_db
from audit import log_action, get_current_username

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    updates = []
    args = []

    for field in ['Name', 'Email', 'ContactNumber']:
        key = field[0].lower() + field[1:]  # camelCase
        if key in data:
            updates.append(f"{field} = %s")
            args.append(data[key])

    # Also handle direct field names
    for field in ['Name', 'Email', 'ContactNumber']:
        if field in data and field not in [u.split(' =')[0] for u in updates]:
            updates.append(f"{field} = %s")
            args.append(data[field])

    if not updates:
        return jsonify(error='No fields to update'), 400

    args.append(user_id)
    execute_db(f"UPDATE Member SET {', '.join(updates)} WHERE MemberID = %s", tuple(args))

    # Update subtype fields if provided
    member = query_db("SELECT MemberType FROM Member WHERE MemberID = %s", (user_id,), one=True)
    if member:
        mt = member['MemberType']
        if mt == 'Student':
            sub_updates = []
            sub_args = []
            for field, key in [('Programme', 'programme'), ('Branch', 'branch'), ('CurrentYear', 'currentYear'), ('MessAssignment', 'messAssignment')]:
                if key in data:
                    sub_updates.append(f"{field} = %s")
                    sub_args.append(data[key])
            if sub_updates:
                sub_args.append(user_id)
                execute_db(f"UPDATE Student SET {', '.join(sub_updates)} WHERE MemberID = %s", tuple(sub_args))

    log_action('UPDATE_PROFILE', f"Updated profile settings: {', '.join(u.split(' =')[0] for u in updates)}", user=get_current_username())
    return jsonify(message='Profile updated')


@settings_bp.route('/password', methods=['PUT'])
@jwt_required()
def change_password():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    current_pw = data.get('currentPassword', '')
    new_pw = data.get('newPassword', '')

    if not current_pw or not new_pw:
        return jsonify(error='Both current and new password required'), 400

    if len(new_pw) < 6:
        return jsonify(error='Password must be at least 6 characters'), 400

    member = query_db("SELECT Password FROM Member WHERE MemberID = %s", (user_id,), one=True)
    if not member or not check_password_hash(member['Password'], current_pw):
        return jsonify(error='Current password is incorrect'), 401

    new_hash = generate_password_hash(new_pw)
    execute_db("UPDATE Member SET Password = %s WHERE MemberID = %s", (new_hash, user_id))
    log_action('CHANGE_PASSWORD', "Password changed", user=get_current_username())
    return jsonify(message='Password changed successfully')


@settings_bp.route('/account', methods=['DELETE'])
@jwt_required()
def delete_account():
    user_id = int(get_jwt_identity())
    log_action('DELETE_ACCOUNT', f"User deleted their own account (MemberID: {user_id})", user=get_current_username())
    execute_db("DELETE FROM Member WHERE MemberID = %s", (user_id,))
    return jsonify(message='Account deleted')

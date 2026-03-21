from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import query_db, execute_db
from audit import log_action, get_current_username

groups_bp = Blueprint('groups', __name__)


@groups_bp.route('/', methods=['GET'])
@jwt_required()
def get_groups():
    user_id = int(get_jwt_identity())
    search = request.args.get('search', '').strip()

    if search:
        rows = query_db("""
            SELECT g.*,
                   (SELECT COUNT(*) FROM GroupMembership WHERE GroupID = g.GroupID) AS memberCount,
                   m.Name AS AdminName
            FROM CampusGroup g
            LEFT JOIN Member m ON g.AdminID = m.MemberID
            WHERE g.Name LIKE %s OR g.Description LIKE %s
            ORDER BY g.GroupID
        """, (f'%{search}%', f'%{search}%'))
    else:
        rows = query_db("""
            SELECT g.*,
                   (SELECT COUNT(*) FROM GroupMembership WHERE GroupID = g.GroupID) AS memberCount,
                   m.Name AS AdminName
            FROM CampusGroup g
            LEFT JOIN Member m ON g.AdminID = m.MemberID
            ORDER BY g.GroupID
        """)

    my_groups = {r['GroupID'] for r in query_db(
        "SELECT GroupID FROM GroupMembership WHERE MemberID = %s", (user_id,)
    )}

    result = []
    for r in rows:
        result.append({
            'GroupID': r['GroupID'],
            'Name': r['Name'],
            'Description': r['Description'],
            'AdminID': r['AdminID'],
            'AdminName': r['AdminName'],
            'memberCount': r['memberCount'],
            'isMember': r['GroupID'] in my_groups,
        })
    return jsonify(result)


@groups_bp.route('/<int:group_id>', methods=['GET'])
@jwt_required()
def get_group(group_id):
    group = query_db("""
        SELECT g.*, m.Name AS AdminName
        FROM CampusGroup g
        LEFT JOIN Member m ON g.AdminID = m.MemberID
        WHERE g.GroupID = %s
    """, (group_id,), one=True)
    if not group:
        return jsonify(error='Group not found'), 404

    members = query_db("""
        SELECT gm.Role, gm.JoinedAt, m.MemberID, m.Username, m.Name, m.MemberType, m.AvatarColor
        FROM GroupMembership gm
        JOIN Member m ON gm.MemberID = m.MemberID
        WHERE gm.GroupID = %s
        ORDER BY FIELD(gm.Role, 'Admin', 'Moderator', 'Member'), gm.JoinedAt
    """, (group_id,))

    return jsonify({
        'GroupID': group['GroupID'],
        'Name': group['Name'],
        'Description': group['Description'],
        'AdminID': group['AdminID'],
        'AdminName': group['AdminName'],
        'members': [{
            'MemberID': m['MemberID'],
            'Username': m['Username'],
            'Name': m['Name'],
            'MemberType': m['MemberType'],
            'avatarColor': m['AvatarColor'],
            'Role': m['Role'],
            'JoinedAt': str(m['JoinedAt']),
        } for m in members],
    })


@groups_bp.route('/<int:group_id>/join', methods=['POST'])
@jwt_required()
def join_group(group_id):
    user_id = int(get_jwt_identity())
    existing = query_db(
        "SELECT * FROM GroupMembership WHERE GroupID = %s AND MemberID = %s",
        (group_id, user_id), one=True,
    )
    if existing:
        return jsonify(error='Already a member'), 409

    execute_db(
        "INSERT INTO GroupMembership (GroupID, MemberID, Role, JoinedAt) VALUES (%s,%s,'Member', CURDATE())",
        (group_id, user_id),
    )
    log_action('JOIN_GROUP', f"Joined group {group_id}", user=get_current_username())
    return jsonify(message='Joined group')


@groups_bp.route('/<int:group_id>/leave', methods=['POST'])
@jwt_required()
def leave_group(group_id):
    user_id = int(get_jwt_identity())
    execute_db(
        "DELETE FROM GroupMembership WHERE GroupID = %s AND MemberID = %s",
        (group_id, user_id),
    )
    log_action('LEAVE_GROUP', f"Left group {group_id}", user=get_current_username())
    return jsonify(message='Left group')


@groups_bp.route('/<int:group_id>/posts', methods=['GET'])
@jwt_required()
def get_group_posts(group_id):
    user_id = int(get_jwt_identity())
    rows = query_db("""
        SELECT p.*, m.Username, m.Name, m.MemberType, m.AvatarColor,
               (SELECT COUNT(*) FROM PostLike WHERE PostID = p.PostID) AS likes,
               (SELECT COUNT(*) FROM Comment WHERE PostID = p.PostID) AS commentCount
        FROM Post p
        JOIN Member m ON p.AuthorID = m.MemberID
        WHERE p.GroupID = %s
        ORDER BY p.CreatedAt DESC
    """, (group_id,))

    liked_posts = {r['PostID'] for r in query_db(
        "SELECT PostID FROM PostLike WHERE MemberID = %s", (user_id,)
    )}

    result = []
    for r in rows:
        result.append({
            'PostID': r['PostID'],
            'AuthorID': r['AuthorID'],
            'GroupID': r['GroupID'],
            'Content': r['Content'],
            'ImageURL': r['ImageURL'],
            'CreatedAt': str(r['CreatedAt']),
            'likes': r['likes'],
            'commentCount': r['commentCount'],
            'liked': r['PostID'] in liked_posts,
            'author': {
                'MemberID': r['AuthorID'],
                'Username': r['Username'],
                'Name': r['Name'],
                'MemberType': r['MemberType'],
                'avatarColor': r['AvatarColor'],
            },
        })
    return jsonify(result)

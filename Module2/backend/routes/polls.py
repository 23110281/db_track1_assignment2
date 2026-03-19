from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import query_db, execute_db
from audit import log_action, get_current_username

polls_bp = Blueprint('polls', __name__)


@polls_bp.route('/', methods=['GET'])
@jwt_required()
def get_polls():
    user_id = int(get_jwt_identity())
    polls = query_db("""
        SELECT p.*, m.Name AS CreatorName, m.AvatarColor
        FROM Poll p
        JOIN Member m ON p.CreatorID = m.MemberID
        ORDER BY p.CreatedAt DESC
    """)

    result = []
    for poll in polls:
        options = query_db("""
            SELECT po.OptionID, po.OptionText,
                   (SELECT COUNT(*) FROM PollVote WHERE OptionID = po.OptionID) AS votes
            FROM PollOption po
            WHERE po.PollID = %s
            ORDER BY po.OptionID
        """, (poll['PollID'],))

        # Check if user already voted on this poll
        user_vote = query_db("""
            SELECT pv.OptionID FROM PollVote pv
            JOIN PollOption po ON pv.OptionID = po.OptionID
            WHERE po.PollID = %s AND pv.MemberID = %s
        """, (poll['PollID'], user_id), one=True)

        result.append({
            'PollID': poll['PollID'],
            'CreatorID': poll['CreatorID'],
            'Question': poll['Question'],
            'CreatedAt': str(poll['CreatedAt']),
            'ExpiresAt': str(poll['ExpiresAt']),
            'CreatorName': poll['CreatorName'],
            'avatarColor': poll['AvatarColor'],
            'options': [{
                'OptionID': o['OptionID'],
                'OptionText': o['OptionText'],
                'votes': o['votes'],
            } for o in options],
            'userVotedOptionId': user_vote['OptionID'] if user_vote else None,
        })
    return jsonify(result)


@polls_bp.route('/', methods=['POST'])
@jwt_required()
def create_poll():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    question = data.get('question', '').strip()
    expires_at = data.get('expiresAt', '')
    options = data.get('options', [])

    if not question or len(options) < 2:
        return jsonify(error='Question and at least 2 options required'), 400

    poll_id = execute_db(
        "INSERT INTO Poll (CreatorID, Question, CreatedAt, ExpiresAt) VALUES (%s,%s, NOW(),%s)",
        (user_id, question, expires_at),
    )
    for opt in options:
        execute_db(
            "INSERT INTO PollOption (PollID, OptionText) VALUES (%s,%s)",
            (poll_id, opt),
        )
    log_action('CREATE_POLL', f"Created poll {poll_id}: '{question}' with {len(options)} options", user=get_current_username())
    return jsonify(pollId=poll_id), 201


@polls_bp.route('/<int:poll_id>/vote', methods=['POST'])
@jwt_required()
def vote_poll(poll_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    option_id = data.get('optionId')

    if not option_id:
        return jsonify(error='optionId required'), 400

    # Check option belongs to this poll
    opt = query_db(
        "SELECT * FROM PollOption WHERE OptionID = %s AND PollID = %s",
        (option_id, poll_id), one=True,
    )
    if not opt:
        return jsonify(error='Invalid option'), 400

    # Remove any existing vote for this poll
    execute_db("""
        DELETE FROM PollVote WHERE MemberID = %s AND OptionID IN
        (SELECT OptionID FROM PollOption WHERE PollID = %s)
    """, (user_id, poll_id))

    execute_db("INSERT INTO PollVote (OptionID, MemberID) VALUES (%s,%s)", (option_id, user_id))
    log_action('VOTE_POLL', f"Voted on poll {poll_id}, option {option_id}", user=get_current_username())
    return jsonify(message='Vote recorded')

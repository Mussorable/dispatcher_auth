from flask import request, jsonify
from flask_jwt_extended import create_access_token

from app import db
from app.main import bp
from app.models import User


@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    existed_user = User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first()
    if existed_user:
        return jsonify({'message': 'User already exists'}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': f'User @{new_user.username} created'}), 201


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    existed_user = User.query.filter_by(username=username).first()
    if existed_user and existed_user.check_password(password):
        access_token = create_access_token(identity={
            'id': existed_user.id,
            'username': existed_user.username,
        })
        return jsonify({'access_token': access_token}), 200

    return jsonify({'message': 'Invalid username or password'}), 401

from gc import callbacks
from typing import final

from flask import request, jsonify
from flask_jwt_extended import create_access_token

from app import db
from app.main import bp
from app.models import User
from app.producer import send_message


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
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

    return jsonify({'message': '/auth/register endpoint'}), 401


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({'message': 'Missing data'}), 400

    username = data.get('username')
    password = data.get('password')

    existed_user = User.query.filter_by(username=username).first()
    if existed_user and existed_user.check_password(password):
        access_token = create_access_token(identity={
            'id': existed_user.id,
            'username': existed_user.username,
        })

        message = {
            'user_id': existed_user.id,
            'access_token': access_token,
            'event': 'login',
        }

        try:
            send_message('user-tokens', message, callback=lambda err, msg: print(err) if err else None)
        except Exception as e:
            # save to log
            print(str(e))

        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'message': 'Invalid username or password'}), 401

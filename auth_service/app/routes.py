# app/routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, get_jwt
)
from . import db
from .models import User, LoginHistory
from .utils import (
    is_token_revoked, revoke_token, jwt_required_with_revocation, redis_client
)
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# 用户注册端点
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({'message': '邮箱已被注册'}), 400

    new_user = User(email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': '用户已注册'}), 201

# 用户登录端点
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user_agent = request.headers.get('User-Agent')

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        # 记录登录历史
        login_history = LoginHistory(user_id=user.id, user_agent=user_agent)
        db.session.add(login_history)
        db.session.commit()

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
    else:
        return jsonify({'message': '无效的凭证'}), 401

# 令牌刷新端点
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token': access_token}), 200

# 用户数据更新端点
@auth_bp.route('/user/update', methods=['PUT'])
@jwt_required_with_revocation
def update_user():
    user_id = get_jwt_identity()
    data = request.get_json()
    new_email = data.get('email')
    new_password = data.get('password')

    user = User.query.get(user_id)

    if new_email:
        if User.query.filter_by(email=new_email).first():
            return jsonify({'message': '邮箱已被使用'}), 400
        user.email = new_email

    if new_password:
        user.set_password(new_password)

    db.session.commit()

    return jsonify({'message': '用户数据已更新'}), 200

# 查看登录历史端点
@auth_bp.route('/user/history', methods=['GET'])
@jwt_required_with_revocation
def login_history():
    user_id = get_jwt_identity()
    history = LoginHistory.query.filter_by(user_id=user_id).all()
    result = []
    for entry in history:
        result.append({
            'user_agent': entry.user_agent,
            'datetime': entry.datetime.isoformat()
        })
    return jsonify(result), 200

# 用户登出端点
@auth_bp.route('/logout', methods=['POST'])
@jwt_required_with_revocation
def logout():
    jwt_payload = get_jwt()
    revoke_token(jwt_payload)
    return jsonify({"message": "成功登出"}), 200

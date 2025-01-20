# app/utils.py

import redis
import os
from flask import jsonify
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt

# 初始化Redis客户端
redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = os.environ.get('REDIS_PORT', 6379)
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=0, decode_responses=True)

def is_token_revoked(jwt_payload):
    """
    检查令牌是否已被吊销
    """
    jti = jwt_payload['jti']
    entry = redis_client.get(jti)
    return entry is not None

def revoke_token(jwt_payload):
    """
    吊销令牌，将其添加到Redis中的黑名单
    """
    jti = jwt_payload['jti']
    redis_client.set(jti, 'true', ex=3600)  # 令牌在1小时内无效

def jwt_required_with_revocation(fn):
    """
    自定义装饰器，检查JWT并验证令牌是否被吊销
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        jwt_payload = get_jwt()
        if is_token_revoked(jwt_payload):
            return jsonify({"msg": "Token has been revoked"}), 401
        return fn(*args, **kwargs)
    return wrapper

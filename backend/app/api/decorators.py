from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def _require_role(role: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            # 兼容旧 token:无 role 声明的视为 admin(历史 token 只可能来自管理员登录)
            current_role = get_jwt().get("role", "admin")
            if current_role != role:
                return jsonify({"code": 403, "msg": "无权访问该接口"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    """要求管理员角色"""
    return _require_role("admin")(fn)


def reader_required(fn):
    """要求学生(读者)角色"""
    return _require_role("reader")(fn)

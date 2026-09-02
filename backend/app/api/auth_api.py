from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    current_user,
)
from marshmallow import ValidationError

from ..extensions import db
from ..models import Admin, LoginSchema, RegisterSchema

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    """登录:校验用户名密码,签发 JWT"""
    try:
        data = LoginSchema().load(request.get_json(force=True, silent=True) or {})
    except ValidationError as e:
        return jsonify({"code": 400, "msg": "参数校验失败", "errors": e.messages}), 400

    admin = Admin.query.filter_by(username=data["username"]).first()
    if not admin or not admin.check_password(data["password"]):
        return jsonify({"code": 401, "msg": "用户名或密码错误"}), 401

    access_token = create_access_token(identity=str(admin.id))
    return jsonify({
        "code": 0,
        "msg": "登录成功",
        "data": {
            "access_token": access_token,
            "user": admin.to_dict(),
        },
    })


@auth_bp.post("/register")
def register():
    """注册管理员(仅 super_admin 可调用)"""
    try:
        data = RegisterSchema().load(request.get_json(force=True, silent=True) or {})
    except ValidationError as e:
        return jsonify({"code": 400, "msg": "参数校验失败", "errors": e.messages}), 400

    if Admin.query.filter_by(username=data["username"]).first():
        return jsonify({"code": 400, "msg": "用户名已存在"}), 400

    admin = Admin(
        username=data["username"],
        real_name=data.get("real_name"),
        role=data.get("role", "admin"),
    )
    admin.set_password(data["password"])
    db.session.add(admin)
    db.session.commit()
    return jsonify({"code": 0, "msg": "注册成功", "data": admin.to_dict()}), 201


@auth_bp.get("/profile")
@jwt_required()
def profile():
    """获取当前登录管理员信息"""
    return jsonify({
        "code": 0,
        "msg": "ok",
        "data": current_user.to_dict() if current_user else None,
    })


@auth_bp.get("/me")
@jwt_required()
def me():
    """profile 的别名"""
    return profile()

from flask import Blueprint, request
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
)
from marshmallow import ValidationError

from ..extensions import db
from ..models import Admin, LoginSchema, RegisterSchema
from ..utils import success, error

auth_bp = Blueprint("auth", __name__)

login_schema = LoginSchema()
register_schema = RegisterSchema()


@auth_bp.post("/login")
def login():
    """管理员登录，返回 JWT"""
    try:
        data = login_schema.load(request.get_json(silent=True) or {})
    except ValidationError as e:
        return error(msg="参数校验失败", code=400, data=e.messages)

    admin = Admin.query.filter_by(username=data["username"]).first()
    if not admin or not admin.check_password(data["password"]):
        return error(msg="用户名或密码错误", code=401)

    access_token = create_access_token(identity=str(admin.id))
    return success(
        data={"access_token": access_token, "user": admin.to_dict()},
        msg="登录成功",
    )


@auth_bp.post("/register")
@jwt_required()
def register():
    """注册新管理员（仅 super_admin 可操作）"""
    identity = get_jwt_identity()
    cur_admin = Admin.query.get(int(identity))
    if not cur_admin or cur_admin.role != "super_admin":
        return error(msg="无权限执行此操作", code=403)

    try:
        data = register_schema.load(request.get_json(silent=True) or {})
    except ValidationError as e:
        return error(msg="参数校验失败", code=400, data=e.messages)

    if Admin.query.filter_by(username=data["username"]).first():
        return error(msg="用户名已存在", code=400)

    admin = Admin(
        username=data["username"],
        real_name=data.get("real_name"),
        role=data.get("role", "admin"),
    )
    admin.set_password(data["password"])
    db.session.add(admin)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error(msg="注册失败", code=500)

    return success(data=admin.to_dict(), msg="注册成功", code=201)


@auth_bp.get("/me")
@jwt_required()
def me():
    """获取当前登录管理员信息"""
    identity = get_jwt_identity()
    admin = Admin.query.get(int(identity))
    if not admin:
        return error(msg="用户不存在", code=404)
    return success(data=admin.to_dict())

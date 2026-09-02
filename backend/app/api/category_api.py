from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from ..extensions import db
from ..models import Category, CategorySchema
from ..utils import success, error

category_bp = Blueprint("category", __name__)

category_schema = CategorySchema()
category_list_schema = CategorySchema(many=True)


@category_bp.get("/")
def list_categories():
    """获取分类列表（支持按名称模糊搜索）"""
    name = request.args.get("name", "").strip()
    q = Category.query
    if name:
        q = q.filter(Category.name.like(f"%{name}%"))
    q = q.order_by(Category.id.asc())
    cats = q.all()
    return success(data=category_list_schema.dump(cats))


@category_bp.get("/<int:cid>")
def get_category(cid):
    """获取单个分类"""
    cat = Category.query.get(cid)
    if not cat:
        return error(msg="分类不存在", code=404)
    return success(data=category_schema.dump(cat))


@category_bp.post("/")
@jwt_required()
def create_category():
    """创建分类"""
    try:
        data = category_schema.load(request.get_json(silent=True) or {})
    except ValidationError as e:
        return error(msg="参数校验失败", code=400, data=e.messages)

    if Category.query.filter_by(name=data["name"]).first():
        return error(msg="分类名已存在", code=400)
    if data.get("code") and Category.query.filter_by(code=data["code"]).first():
        return error(msg="分类编码已存在", code=400)

    cat = Category(**data)
    db.session.add(cat)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error(msg="创建失败", code=500)

    return success(data=category_schema.dump(cat), msg="创建成功", code=201)


@category_bp.put("/<int:cid>")
@jwt_required()
def update_category(cid):
    """更新分类"""
    cat = Category.query.get(cid)
    if not cat:
        return error(msg="分类不存在", code=404)

    try:
        data = category_schema.load(request.get_json(silent=True) or {}, partial=True)
    except ValidationError as e:
        return error(msg="参数校验失败", code=400, data=e.messages)

    if "name" in data and data["name"] != cat.name:
        if Category.query.filter_by(name=data["name"]).first():
            return error(msg="分类名已存在", code=400)
    if "code" in data and data["code"] and data["code"] != cat.code:
        if Category.query.filter_by(code=data["code"]).first():
            return error(msg="分类编码已存在", code=400)

    for k, v in data.items():
        setattr(cat, k, v)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error(msg="更新失败", code=500)

    return success(data=category_schema.dump(cat), msg="更新成功")


@category_bp.delete("/<int:cid>")
@jwt_required()
def delete_category(cid):
    """删除分类（若仍有图书关联则拒绝）"""
    cat = Category.query.get(cid)
    if not cat:
        return error(msg="分类不存在", code=404)

    if cat.books.count() > 0:
        return error(msg="该分类下还有图书，无法删除", code=400)

    db.session.delete(cat)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error(msg="删除失败", code=500)

    return success(msg="删除成功")

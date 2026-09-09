from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from ..extensions import db
from ..models import Category, CategorySchema
from ..config import Config

category_bp = Blueprint("category", __name__)


def _paginate(query):
    """统一分页:支持 ?page & ?page_size,默认值取自配置"""
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(
        max(int(request.args.get("page_size", Config.DEFAULT_PAGE_SIZE)), 1),
        Config.MAX_PAGE_SIZE,
    )
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    return {
        "items": [item.to_dict() for item in pagination.items],
        "total": pagination.total,
        "page": page,
        "page_size": page_size,
        "pages": pagination.pages,
    }


@category_bp.get("")
def list_categories():
    """分类列表:支持分页,默认返回全部(无分页参数时)"""
    q = Category.query.order_by(Category.id.desc())
    if request.args.get("page") or request.args.get("page_size"):
        return jsonify({"code": 0, "msg": "ok", "data": _paginate(q)})
    return jsonify({
        "code": 0,
        "msg": "ok",
        "data": {"items": [c.to_dict() for c in q.all()], "total": q.count()},
    })


@category_bp.get("/<int:cid>")
def get_category(cid):
    cat = Category.query.get_or_404(cid)
    return jsonify({"code": 0, "msg": "ok", "data": cat.to_dict()})


@category_bp.post("")
def create_category():
    try:
        data = CategorySchema().load(request.get_json(force=True, silent=True) or {})
    except ValidationError as e:
        return jsonify({"code": 400, "msg": "参数校验失败", "errors": e.messages}), 400

    if data.get("code") and Category.query.filter_by(code=data["code"]).first():
        return jsonify({"code": 400, "msg": "分类编码已存在"}), 400

    cat = Category(**data)
    db.session.add(cat)
    db.session.commit()
    return jsonify({"code": 0, "msg": "创建成功", "data": cat.to_dict()}), 201


@category_bp.put("/<int:cid>")
def update_category(cid):
    cat = Category.query.get_or_404(cid)
    try:
        data = CategorySchema().load(request.get_json(force=True, silent=True) or {},
                                     partial=True)
    except ValidationError as e:
        return jsonify({"code": 400, "msg": "参数校验失败", "errors": e.messages}), 400

    for k, v in data.items():
        setattr(cat, k, v)
    db.session.commit()
    return jsonify({"code": 0, "msg": "更新成功", "data": cat.to_dict()})


@category_bp.delete("/<int:cid>")
def delete_category(cid):
    cat = Category.query.get_or_404(cid)
    db.session.delete(cat)
    db.session.commit()
    return jsonify({"code": 0, "msg": "删除成功"})

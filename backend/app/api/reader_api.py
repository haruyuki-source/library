from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from ..extensions import db
from ..models import Reader, ReaderSchema
from ..config import Config

reader_bp = Blueprint("reader", __name__)


def _paginate(query):
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(
        max(int(request.args.get("page_size", Config.DEFAULT_PAGE_SIZE)), 1),
        Config.MAX_PAGE_SIZE,
    )
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    return {
        "items": [r.to_dict() for r in pagination.items],
        "total": pagination.total,
        "page": page,
        "page_size": page_size,
        "pages": pagination.pages,
    }


@reader_bp.get("")
def list_readers():
    """读者列表:支持 keyword(姓名/借阅证号/手机) + 分页"""
    q = Reader.query.order_by(Reader.id.desc())

    keyword = (request.args.get("keyword") or "").strip()
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(
            db.or_(Reader.name.ilike(like), Reader.card_no.ilike(like),
                   Reader.phone.ilike(like))
        )

    status = request.args.get("status")
    if status:
        q = q.filter_by(status=status)

    return jsonify({"code": 0, "msg": "ok", "data": _paginate(q)})


@reader_bp.get("/<int:rid>")
def get_reader(rid):
    reader = Reader.query.get_or_404(rid)
    return jsonify({"code": 0, "msg": "ok", "data": reader.to_dict()})


@reader_bp.post("")
def create_reader():
    try:
        data = ReaderSchema().load(request.get_json(force=True, silent=True) or {})
    except ValidationError as e:
        return jsonify({"code": 400, "msg": "参数校验失败", "errors": e.messages}), 400

    if Reader.query.filter_by(card_no=data["card_no"]).first():
        return jsonify({"code": 400, "msg": "借阅证号已存在"}), 400

    reader = Reader(**data)
    db.session.add(reader)
    db.session.commit()
    return jsonify({"code": 0, "msg": "创建成功", "data": reader.to_dict()}), 201


@reader_bp.put("/<int:rid>")
def update_reader(rid):
    reader = Reader.query.get_or_404(rid)
    try:
        data = ReaderSchema().load(request.get_json(force=True, silent=True) or {},
                                   partial=True)
    except ValidationError as e:
        return jsonify({"code": 400, "msg": "参数校验失败", "errors": e.messages}), 400

    for k, v in data.items():
        setattr(reader, k, v)
    db.session.commit()
    return jsonify({"code": 0, "msg": "更新成功", "data": reader.to_dict()})


@reader_bp.delete("/<int:rid>")
def delete_reader(rid):
    reader = Reader.query.get_or_404(rid)
    db.session.delete(reader)
    db.session.commit()
    return jsonify({"code": 0, "msg": "删除成功"})

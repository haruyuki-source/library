from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from sqlalchemy import or_

from ..config import Config
from ..extensions import db
from ..models import Reader, ReaderSchema, BorrowRecord
from ..utils import success, error, paginate

reader_bp = Blueprint("reader", __name__)

reader_schema = ReaderSchema()
reader_list_schema = ReaderSchema(many=True)


@reader_bp.get("/")
def list_readers():
    """读者列表（分页 + 关键字 / 状态 / 部门筛选）"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", Config.DEFAULT_PAGE_SIZE, type=int)
    per_page = min(max(per_page, 1), Config.MAX_PAGE_SIZE)

    keyword = request.args.get("keyword", "").strip()
    status = request.args.get("status", "").strip()
    department = request.args.get("department", "").strip()

    q = Reader.query
    if keyword:
        q = q.filter(or_(
            Reader.name.like(f"%{keyword}%"),
            Reader.card_no.like(f"%{keyword}%"),
            Reader.phone.like(f"%{keyword}%"),
        ))
    if status:
        q = q.filter(Reader.status == status)
    if department:
        q = q.filter(Reader.department.like(f"%{department}%"))
    q = q.order_by(Reader.id.desc())

    data = paginate(q, page, per_page, serializer=lambda r: r.to_dict())
    return success(data=data)


@reader_bp.get("/<int:rid>")
def get_reader(rid):
    """获取单个读者（含当前在借数量）"""
    reader = Reader.query.get(rid)
    if not reader:
        return error(msg="读者不存在", code=404)

    active_count = reader.borrow_records.filter(
        BorrowRecord.status.in_(["borrowed", "overdue"])
    ).count()
    data = reader.to_dict()
    data["current_borrow_count"] = active_count
    return success(data=data)


@reader_bp.post("/")
@jwt_required()
def create_reader():
    """创建读者"""
    try:
        data = reader_schema.load(request.get_json(silent=True) or {})
    except ValidationError as e:
        return error(msg="参数校验失败", code=400, data=e.messages)

    if Reader.query.filter_by(card_no=data["card_no"]).first():
        return error(msg="借阅证号已存在", code=400)

    reader = Reader(**data)
    db.session.add(reader)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error(msg="创建失败", code=500)

    return success(data=reader.to_dict(), msg="创建成功", code=201)


@reader_bp.put("/<int:rid>")
@jwt_required()
def update_reader(rid):
    """更新读者"""
    reader = Reader.query.get(rid)
    if not reader:
        return error(msg="读者不存在", code=404)

    try:
        data = reader_schema.load(request.get_json(silent=True) or {}, partial=True)
    except ValidationError as e:
        return error(msg="参数校验失败", code=400, data=e.messages)

    if "card_no" in data and data["card_no"] != reader.card_no:
        if Reader.query.filter_by(card_no=data["card_no"]).first():
            return error(msg="借阅证号已存在", code=400)

    for k, v in data.items():
        setattr(reader, k, v)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error(msg="更新失败", code=500)

    return success(data=reader.to_dict(), msg="更新成功")


@reader_bp.delete("/<int:rid>")
@jwt_required()
def delete_reader(rid):
    """删除读者（有未归还借阅时拒绝）"""
    reader = Reader.query.get(rid)
    if not reader:
        return error(msg="读者不存在", code=404)

    active = reader.borrow_records.filter(
        BorrowRecord.status.in_(["borrowed", "overdue"])
    ).count()
    if active > 0:
        return error(msg="该读者有未归还的借阅记录，无法删除", code=400)

    db.session.delete(reader)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error(msg="删除失败", code=500)

    return success(msg="删除成功")

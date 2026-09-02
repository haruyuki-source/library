from datetime import date, timedelta

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from marshmallow import ValidationError

from ..extensions import db
from ..models import BorrowRecord, Book, Reader, BorrowSchema, ReturnSchema, RenewSchema
from ..config import Config

borrow_bp = Blueprint("borrow", __name__)


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


@borrow_bp.get("")
def list_borrows():
    """借阅记录列表:支持 status 过滤 + 分页"""
    q = BorrowRecord.query.order_by(BorrowRecord.id.desc())

    status = request.args.get("status")
    if status:
        q = q.filter_by(status=status)

    reader_id = request.args.get("reader_id")
    if reader_id:
        q = q.filter_by(reader_id=int(reader_id))

    book_id = request.args.get("book_id")
    if book_id:
        q = q.filter_by(book_id=int(book_id))

    return jsonify({"code": 0, "msg": "ok", "data": _paginate(q)})


@borrow_bp.get("/<int:rid>")
def get_borrow(rid):
    rec = BorrowRecord.query.get_or_404(rid)
    return jsonify({"code": 0, "msg": "ok", "data": rec.to_dict()})


@borrow_bp.post("")
@jwt_required()
def create_borrow():
    """借书:校验图书库存与读者借阅上限,生成借阅记录"""
    try:
        data = BorrowSchema().load(request.get_json(force=True, silent=True) or {})
    except ValidationError as e:
        return jsonify({"code": 400, "msg": "参数校验失败", "errors": e.messages}), 400

    book = Book.query.get(data["book_id"])
    reader = Reader.query.get(data["reader_id"])
    if not book:
        return jsonify({"code": 404, "msg": "图书不存在"}), 404
    if not reader:
        return jsonify({"code": 404, "msg": "读者不存在"}), 404
    if book.available_quantity <= 0:
        return jsonify({"code": 400, "msg": "图书库存不足"}), 400

    # 读者当前未归还数量
    active_count = BorrowRecord.query.filter_by(
        reader_id=reader.id, status="borrowed"
    ).count()
    if active_count >= reader.max_borrow:
        return jsonify({"code": 400, "msg": f"已达借阅上限({reader.max_borrow} 本)"}), 400

    borrow_date = data.get("borrow_date") or date.today()
    due_days = data.get("due_days", 30)
    due_date = borrow_date + timedelta(days=due_days)

    rec = BorrowRecord(
        reader_id=reader.id,
        book_id=book.id,
        admin_id=int(get_jwt_identity()) if get_jwt_identity() else None,
        borrow_date=borrow_date,
        due_date=due_date,
        remark=data.get("remark"),
        status="borrowed",
    )
    book.available_quantity -= 1
    db.session.add(rec)
    db.session.commit()
    return jsonify({"code": 0, "msg": "借阅成功", "data": rec.to_dict()}), 201


@borrow_bp.put("/<int:rid>/return")
@jwt_required()
def return_book(rid):
    """还书:记录归还日期,归还库存,计算逾期罚金"""
    rec = BorrowRecord.query.get_or_404(rid)
    if rec.status == "returned":
        return jsonify({"code": 400, "msg": "该书已归还"}), 400

    body = request.get_json(silent=True) or {}
    rec.return_date = date.today()
    rec.status = "overdue" if rec.return_date > rec.due_date else "returned"
    rec.fine_amount = rec.calculate_fine()
    if body.get("remark"):
        rec.remark = body["remark"]

    # 归还库存
    book = Book.query.get(rec.book_id)
    if book:
        book.available_quantity += 1

    db.session.commit()
    return jsonify({"code": 0, "msg": "归还成功", "data": rec.to_dict()})


@borrow_bp.put("/<int:rid>/renew")
@jwt_required()
def renew_book(rid):
    """续借:延长应还日期,续借次数 +1"""
    rec = BorrowRecord.query.get_or_404(rid)
    if rec.status != "borrowed":
        return jsonify({"code": 400, "msg": "仅借阅中的记录可续借"}), 400

    try:
        data = RenewSchema().load(request.get_json(force=True, silent=True) or {})
    except ValidationError as e:
        return jsonify({"code": 400, "msg": "参数校验失败", "errors": e.messages}), 400

    extra = data.get("extra_days", 30)
    rec.due_date = (rec.due_date or date.today()) + timedelta(days=extra)
    rec.renew_count = (rec.renew_count or 0) + 1
    db.session.commit()
    return jsonify({"code": 0, "msg": "续借成功", "data": rec.to_dict()})


@borrow_bp.delete("/<int:rid>")
@jwt_required()
def delete_borrow(rid):
    """删除借阅记录:若记录仍在借阅中,需归还库存"""
    rec = BorrowRecord.query.get_or_404(rid)
    if rec.status in ("borrowed", "overdue"):
        book = Book.query.get(rec.book_id)
        if book:
            book.available_quantity += 1
    db.session.delete(rec)
    db.session.commit()
    return jsonify({"code": 0, "msg": "删除成功"})

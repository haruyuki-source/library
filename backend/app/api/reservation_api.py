from datetime import date, timedelta

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from ..extensions import db
from ..models import Reservation, BorrowRecord, Book, Reader
from ..config import Config
from .decorators import admin_required

reservation_bp = Blueprint("reservation", __name__)

# 到馆确认借书后的借阅期限(天)
BORROW_DAYS = 30
# 在借状态:borrowed 正常在借,overdue 超期未还
ACTIVE_STATUSES = ("borrowed", "overdue")


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


@reservation_bp.get("")
@admin_required
def list_reservations():
    """预约列表:支持 status / reader_id / book_id 过滤 + 分页"""
    q = Reservation.query.order_by(Reservation.id.desc())

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


@reservation_bp.get("/<int:rid>")
@admin_required
def get_reservation(rid):
    rec = Reservation.query.get_or_404(rid)
    return jsonify({"code": 0, "msg": "ok", "data": rec.to_dict()})


@reservation_bp.put("/<int:rid>/fulfill")
@admin_required
def fulfill_reservation(rid):
    """到馆办理:预约转借阅。唯一的扣库存入口——校验通过后在同一事务内
    创建借阅记录 + 扣减可借库存 + 更新预约状态,任一步失败整体回滚。"""
    rec = Reservation.query.get_or_404(rid)
    if rec.status != Reservation.RESERVED:
        return jsonify({"code": 400, "msg": "仅预约中的记录可办理借书"}), 400

    reader = Reader.query.get(rec.reader_id)
    book = Book.query.get(rec.book_id)
    if not reader:
        return jsonify({"code": 404, "msg": "读者不存在"}), 404
    if not book:
        return jsonify({"code": 404, "msg": "图书不存在"}), 404
    if reader.status != "active":
        return jsonify({"code": 403, "msg": "该读者账户已被停用,无法办理"}), 403

    # 防止读者已在别处借了同一本书
    dup_borrow = BorrowRecord.query.filter(
        BorrowRecord.reader_id == reader.id,
        BorrowRecord.book_id == book.id,
        BorrowRecord.status.in_(ACTIVE_STATUSES),
    ).first()
    if dup_borrow:
        return jsonify({"code": 400, "msg": "该读者已借阅此书且尚未归还"}), 400

    active_count = BorrowRecord.query.filter(
        BorrowRecord.reader_id == reader.id,
        BorrowRecord.status.in_(ACTIVE_STATUSES),
    ).count()
    if active_count >= reader.max_borrow:
        return jsonify(
            {"code": 400, "msg": f"该读者已达借阅上限({reader.max_borrow} 本)"}
        ), 400

    if (book.available_quantity or 0) <= 0:
        return jsonify({"code": 400, "msg": "该书当前无可用库存,无法办理,请稍后再来或调配馆藏"}), 400

    admin_id = int(get_jwt_identity()) if get_jwt_identity() else None
    borrow_date = date.today()
    try:
        borrow_rec = BorrowRecord(
            reader_id=reader.id,
            book_id=book.id,
            admin_id=admin_id,
            borrow_date=borrow_date,
            due_date=borrow_date + timedelta(days=BORROW_DAYS),
            status="borrowed",
        )
        db.session.add(borrow_rec)
        book.available_quantity -= 1
        db.session.flush()  # 取得 borrow_rec.id 并尽早暴露约束错误
        rec.status = Reservation.FULFILLED
        rec.fulfill_date = borrow_date
        rec.borrow_record_id = borrow_rec.id
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({
        "code": 0,
        "msg": "办理成功,已转为借阅并扣减库存",
        "data": {"reservation": rec.to_dict(), "borrow_record": borrow_rec.to_dict()},
    })


@reservation_bp.put("/<int:rid>/cancel")
@admin_required
def cancel_reservation(rid):
    """管理员取消预约(读者失约/放弃等),预约不涉及库存,无需回补"""
    rec = Reservation.query.get_or_404(rid)
    if rec.status != Reservation.RESERVED:
        return jsonify({"code": 400, "msg": "仅预约中的记录可取消"}), 400

    rec.status = Reservation.CANCELLED
    db.session.commit()
    return jsonify({"code": 0, "msg": "预约已取消", "data": rec.to_dict()})

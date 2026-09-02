from datetime import date, timedelta

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from ..config import Config
from ..extensions import db
from ..models import (
    Admin, Book, BorrowRecord, Reader,
    BorrowSchema, RenewSchema, ReturnSchema,
)
from ..utils import success, error, paginate

borrow_bp = Blueprint("borrow", __name__)

borrow_schema = BorrowSchema()
renew_schema = RenewSchema()
return_schema = ReturnSchema()

# 续借次数上限
MAX_RENEW_COUNT = 2
# 逾期每日罚金
DAILY_FINE_RATE = 0.5


@borrow_bp.post("/")
@jwt_required()
def borrow_book():
    """借书：校验读者状态、库存、借阅上限，并扣减可借库存"""
    try:
        data = borrow_schema.load(request.get_json(silent=True) or {})
    except ValidationError as e:
        return error(msg="参数校验失败", code=400, data=e.messages)

    reader = Reader.query.get(data["reader_id"])
    if not reader:
        return error(msg="读者不存在", code=404)
    if reader.status != "active":
        return error(msg="读者已被禁用，无法借阅", code=400)

    book = Book.query.get(data["book_id"])
    if not book:
        return error(msg="图书不存在", code=404)
    if book.available_quantity <= 0:
        return error(msg="图书库存不足", code=400)

    # 借阅数量上限校验
    active_count = reader.borrow_records.filter(
        BorrowRecord.status.in_(["borrowed", "overdue"])
    ).count()
    if active_count >= reader.max_borrow:
        return error(msg=f"已达借阅上限({reader.max_borrow}本)", code=400)

    # 同一本书未归还不可重复借阅
    already = reader.borrow_records.filter_by(
        book_id=book.id, status="borrowed"
    ).first()
    if already:
        return error(msg="已借阅此书且未归还", code=400)

    admin_id = get_jwt_identity()
    admin = Admin.query.get(int(admin_id)) if admin_id else None

    borrow_date = data.get("borrow_date") or date.today()
    due_days = data.get("due_days", 30)
    due_date = borrow_date + timedelta(days=due_days)

    record = BorrowRecord(
        reader_id=reader.id,
        book_id=book.id,
        admin_id=admin.id if admin else None,
        borrow_date=borrow_date,
        due_date=due_date,
        status="borrowed",
        remark=data.get("remark"),
    )
    book.available_quantity -= 1

    db.session.add(record)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error(msg="借阅失败", code=500)

    return success(data=record.to_dict(), msg="借阅成功", code=201)


@borrow_bp.post("/return")
@jwt_required()
def return_book():
    """还书：归还日期、库存回补、罚金计算"""
    try:
        data = return_schema.load(request.get_json(silent=True) or {})
    except ValidationError as e:
        return error(msg="参数校验失败", code=400, data=e.messages)

    record = BorrowRecord.query.get(data["record_id"])
    if not record:
        return error(msg="借阅记录不存在", code=404)
    if record.status == "returned":
        return error(msg="该书已归还", code=400)

    book = record.book_ref
    if book:
        book.available_quantity = min(
            book.available_quantity + 1, book.total_quantity
        )

    record.return_date = date.today()
    # 逾期归还时仍记为 returned，但写入罚金
    if record.return_date > record.due_date:
        days = (record.return_date - record.due_date).days
        record.fine_amount = round(days * DAILY_FINE_RATE, 2)
    record.status = "returned"

    if data.get("remark"):
        record.remark = data["remark"]

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error(msg="归还失败", code=500)

    return success(data=record.to_dict(), msg="归还成功")


@borrow_bp.post("/renew")
@jwt_required()
def renew_book():
    """续借：延长应还日期，限制续借次数"""
    try:
        data = renew_schema.load(request.get_json(silent=True) or {})
    except ValidationError as e:
        return error(msg="参数校验失败", code=400, data=e.messages)

    record = BorrowRecord.query.get(data["record_id"])
    if not record:
        return error(msg="借阅记录不存在", code=404)
    if record.status != "borrowed":
        return error(msg="该书已归还或状态不允许续借", code=400)
    if record.renew_count >= MAX_RENEW_COUNT:
        return error(msg=f"已达续借次数上限({MAX_RENEW_COUNT}次)", code=400)

    extra_days = data.get("extra_days", 30)
    record.due_date = record.due_date + timedelta(days=extra_days)
    record.renew_count += 1

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error(msg="续借失败", code=500)

    return success(data=record.to_dict(), msg="续借成功")


@borrow_bp.get("/")
def list_records():
    """借阅记录列表（分页 + 读者 / 图书 / 状态筛选）"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", Config.DEFAULT_PAGE_SIZE, type=int)
    per_page = min(max(per_page, 1), Config.MAX_PAGE_SIZE)

    reader_id = request.args.get("reader_id", type=int)
    book_id = request.args.get("book_id", type=int)
    status = request.args.get("status", "").strip()

    q = BorrowRecord.query
    if reader_id:
        q = q.filter(BorrowRecord.reader_id == reader_id)
    if book_id:
        q = q.filter(BorrowRecord.book_id == book_id)
    if status:
        q = q.filter(BorrowRecord.status == status)
    q = q.order_by(BorrowRecord.id.desc())

    data = paginate(q, page, per_page, serializer=lambda r: r.to_dict())
    return success(data=data)


@borrow_bp.get("/<int:rid>")
def get_record(rid):
    """获取单条借阅记录"""
    record = BorrowRecord.query.get(rid)
    if not record:
        return error(msg="借阅记录不存在", code=404)
    return success(data=record.to_dict())


@borrow_bp.get("/reader/<int:reader_id>")
def reader_records(reader_id):
    """获取指定读者的全部借阅记录"""
    reader = Reader.query.get(reader_id)
    if not reader:
        return error(msg="读者不存在", code=404)
    records = reader.borrow_records.order_by(BorrowRecord.id.desc()).all()
    return success(data=[r.to_dict() for r in records])


@borrow_bp.get("/overdue")
def overdue_records():
    """获取当前逾期未还记录（动态计算应缴罚金，不改写状态）"""
    today = date.today()
    records = (
        BorrowRecord.query
        .filter(BorrowRecord.status == "borrowed", BorrowRecord.due_date < today)
        .order_by(BorrowRecord.due_date.asc())
        .all()
    )
    data = []
    for r in records:
        item = r.to_dict()
        item["current_fine"] = r.calculate_fine(daily_rate=DAILY_FINE_RATE)
        data.append(item)
    return success(data=data)

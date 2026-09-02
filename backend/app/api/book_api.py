from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from sqlalchemy import or_

from ..config import Config
from ..extensions import db
from ..models import Book, BookSchema, BorrowRecord
from ..utils import success, error, paginate

book_bp = Blueprint("book", __name__)

book_schema = BookSchema()
book_list_schema = BookSchema(many=True)


@book_bp.get("/")
def list_books():
    """图书列表（分页 + 关键字 / 分类 / 作者筛选）"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", Config.DEFAULT_PAGE_SIZE, type=int)
    per_page = min(max(per_page, 1), Config.MAX_PAGE_SIZE)

    keyword = request.args.get("keyword", "").strip()
    category_id = request.args.get("category_id", type=int)
    author = request.args.get("author", "").strip()

    q = Book.query
    if keyword:
        q = q.filter(or_(
            Book.title.like(f"%{keyword}%"),
            Book.isbn.like(f"%{keyword}%"),
        ))
    if category_id:
        q = q.filter(Book.category_id == category_id)
    if author:
        q = q.filter(Book.author.like(f"%{author}%"))
    q = q.order_by(Book.id.desc())

    data = paginate(q, page, per_page, serializer=lambda b: b.to_dict())
    return success(data=data)


@book_bp.get("/<int:bid>")
def get_book(bid):
    """获取单个图书"""
    book = Book.query.get(bid)
    if not book:
        return error(msg="图书不存在", code=404)
    return success(data=book.to_dict())


@book_bp.post("/")
@jwt_required()
def create_book():
    """创建图书"""
    try:
        data = book_schema.load(request.get_json(silent=True) or {})
    except ValidationError as e:
        return error(msg="参数校验失败", code=400, data=e.messages)

    if data.get("isbn") and Book.query.filter_by(isbn=data["isbn"]).first():
        return error(msg="ISBN 已存在", code=400)

    # 保证 available 不超过 total
    total = data.get("total_quantity", 1)
    avail = data.get("available_quantity", total)
    if avail > total:
        avail = total
    data["total_quantity"] = total
    data["available_quantity"] = avail

    book = Book(**data)
    db.session.add(book)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error(msg="创建失败", code=500)

    return success(data=book.to_dict(), msg="创建成功", code=201)


@book_bp.put("/<int:bid>")
@jwt_required()
def update_book(bid):
    """更新图书"""
    book = Book.query.get(bid)
    if not book:
        return error(msg="图书不存在", code=404)

    try:
        data = book_schema.load(request.get_json(silent=True) or {}, partial=True)
    except ValidationError as e:
        return error(msg="参数校验失败", code=400, data=e.messages)

    if "isbn" in data and data["isbn"] and data["isbn"] != book.isbn:
        if Book.query.filter_by(isbn=data["isbn"]).first():
            return error(msg="ISBN 已存在", code=400)

    # 校验库存关系
    new_total = data.get("total_quantity", book.total_quantity)
    new_avail = data.get("available_quantity", book.available_quantity)
    if new_avail > new_total:
        return error(msg="可借数量不能大于总库存", code=400)

    for k, v in data.items():
        if k == "category":
            continue
        setattr(book, k, v)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error(msg="更新失败", code=500)

    return success(data=book.to_dict(), msg="更新成功")


@book_bp.delete("/<int:bid>")
@jwt_required()
def delete_book(bid):
    """删除图书（有未归还借阅时拒绝）"""
    book = Book.query.get(bid)
    if not book:
        return error(msg="图书不存在", code=404)

    active = book.borrow_records.filter(
        BorrowRecord.status.in_(["borrowed", "overdue"])
    ).count()
    if active > 0:
        return error(msg="该图书有未归还的借阅记录，无法删除", code=400)

    db.session.delete(book)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error(msg="删除失败", code=500)

    return success(msg="删除成功")

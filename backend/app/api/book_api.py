from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from ..extensions import db
from ..models import Book, BookSchema
from ..config import Config

book_bp = Blueprint("book", __name__)


def _paginate(query):
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(
        max(int(request.args.get("page_size", Config.DEFAULT_PAGE_SIZE)), 1),
        Config.MAX_PAGE_SIZE,
    )
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    return {
        "items": [b.to_dict() for b in pagination.items],
        "total": pagination.total,
        "page": page,
        "page_size": page_size,
        "pages": pagination.pages,
    }


@book_bp.get("")
def list_books():
    """图书列表:支持 keyword(书名/作者/ISBN)、category_id 过滤 + 分页"""
    q = Book.query.order_by(Book.id.desc())

    keyword = (request.args.get("keyword") or "").strip()
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(
            db.or_(Book.title.ilike(like), Book.author.ilike(like), Book.isbn.ilike(like))
        )

    cat_id = request.args.get("category_id")
    if cat_id:
        q = q.filter_by(category_id=int(cat_id))

    return jsonify({"code": 0, "msg": "ok", "data": _paginate(q)})


@book_bp.get("/<int:bid>")
def get_book(bid):
    book = Book.query.get_or_404(bid)
    return jsonify({"code": 0, "msg": "ok", "data": book.to_dict()})


@book_bp.post("")
def create_book():
    try:
        data = BookSchema().load(request.get_json(force=True, silent=True) or {})
    except ValidationError as e:
        return jsonify({"code": 400, "msg": "参数校验失败", "errors": e.messages}), 400

    book = Book(**data)
    # 新建时可用库存默认等于总库存
    if book.available_quantity is None:
        book.available_quantity = book.total_quantity
    db.session.add(book)
    db.session.commit()
    return jsonify({"code": 0, "msg": "创建成功", "data": book.to_dict()}), 201


@book_bp.put("/<int:bid>")
def update_book(bid):
    book = Book.query.get_or_404(bid)
    try:
        data = BookSchema().load(request.get_json(force=True, silent=True) or {},
                                 partial=True)
    except ValidationError as e:
        return jsonify({"code": 400, "msg": "参数校验失败", "errors": e.messages}), 400

    for k, v in data.items():
        setattr(book, k, v)
    db.session.commit()
    return jsonify({"code": 0, "msg": "更新成功", "data": book.to_dict()})


@book_bp.delete("/<int:bid>")
def delete_book(bid):
    book = Book.query.get_or_404(bid)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"code": 0, "msg": "删除成功"})

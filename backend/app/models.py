from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import Schema, fields, validate, validates, ValidationError, post_load

from .extensions import db


# ============================================================
# Models
# ============================================================

class Admin(db.Model):
    """管理员/图书管理员（登录系统的用户）"""
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    real_name = db.Column(db.String(64))
    role = db.Column(db.String(20), default="admin")  # admin / super_admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "real_name": self.real_name,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Category(db.Model):
    """图书分类"""
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)
    code = db.Column(db.String(32), unique=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    books = db.relationship("Book", backref="category_ref", lazy="dynamic")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Reader(db.Model):
    """读者"""
    __tablename__ = "readers"

    id = db.Column(db.Integer, primary_key=True)
    card_no = db.Column(db.String(32), unique=True, nullable=False, index=True)  # 借阅证号
    name = db.Column(db.String(64), nullable=False)
    gender = db.Column(db.String(8))  # male / female / other
    phone = db.Column(db.String(20))
    email = db.Column(db.String(128))
    department = db.Column(db.String(128))  # 学院/部门
    status = db.Column(db.String(16), default="active")  # active / disabled
    max_borrow = db.Column(db.Integer, default=5)  # 最大借阅数量
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    borrow_records = db.relationship("BorrowRecord", backref="reader_ref", lazy="dynamic")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "card_no": self.card_no,
            "name": self.name,
            "gender": self.gender,
            "phone": self.phone,
            "email": self.email,
            "department": self.department,
            "status": self.status,
            "max_borrow": self.max_borrow,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Book(db.Model):
    """图书"""
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(32), index=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    author = db.Column(db.String(128))
    publisher = db.Column(db.String(128))
    publish_year = db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), index=True)
    location = db.Column(db.String(64))  # 馆藏位置
    total_quantity = db.Column(db.Integer, default=1)
    available_quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, default=0.0)
    description = db.Column(db.Text)
    cover_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    borrow_records = db.relationship("BorrowRecord", backref="book_ref", lazy="dynamic")

    def to_dict(self, include_category: bool = True) -> dict:
        data = {
            "id": self.id,
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "publisher": self.publisher,
            "publish_year": self.publish_year,
            "category_id": self.category_id,
            "location": self.location,
            "total_quantity": self.total_quantity,
            "available_quantity": self.available_quantity,
            "price": self.price,
            "description": self.description,
            "cover_url": self.cover_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_category and self.category_ref:
            data["category"] = self.category_ref.to_dict()
        return data


class BorrowRecord(db.Model):
    """借阅记录"""
    __tablename__ = "borrow_records"

    id = db.Column(db.Integer, primary_key=True)
    reader_id = db.Column(db.Integer, db.ForeignKey("readers.id"), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False, index=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"))

    borrow_date = db.Column(db.Date, default=date.today, nullable=False)
    due_date = db.Column(db.Date, nullable=False)  # 应还日期
    return_date = db.Column(db.Date)  # 实际归还日期

    renew_count = db.Column(db.Integer, default=0)  # 续借次数
    status = db.Column(db.String(16), default="borrowed")  # borrowed / returned / overdue / lost
    fine_amount = db.Column(db.Float, default=0.0)  # 罚金
    fine_paid = db.Column(db.Boolean, default=False)

    remark = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    admin = db.relationship("Admin", backref="borrow_records")
    # book_ref, reader_ref backref 由 Book / Reader 定义

    def calculate_fine(self, daily_rate: float = 0.5) -> float:
        """根据当前日期或归还日期计算逾期罚金"""
        if self.status == "borrowed":
            today = date.today()
            if today > self.due_date:
                days = (today - self.due_date).days
                return round(days * daily_rate, 2)
            return 0.0
        if self.status == "overdue" and self.return_date:
            days = (self.return_date - self.due_date).days
            return round(max(days, 0) * daily_rate, 2)
        return self.fine_amount

    def to_dict(self, include_reader: bool = True, include_book: bool = True) -> dict:
        data = {
            "id": self.id,
            "reader_id": self.reader_id,
            "book_id": self.book_id,
            "admin_id": self.admin_id,
            "borrow_date": self.borrow_date.isoformat() if self.borrow_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "return_date": self.return_date.isoformat() if self.return_date else None,
            "renew_count": self.renew_count,
            "status": self.status,
            "fine_amount": self.fine_amount,
            "fine_paid": self.fine_paid,
            "remark": self.remark,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_reader and self.reader_ref:
            data["reader"] = {
                "id": self.reader_ref.id,
                "card_no": self.reader_ref.card_no,
                "name": self.reader_ref.name,
            }
        if include_book and self.book_ref:
            data["book"] = {
                "id": self.book_ref.id,
                "isbn": self.book_ref.isbn,
                "title": self.book_ref.title,
                "author": self.book_ref.author,
            }
        return data


# ============================================================
# Marshmallow Schemas (validation + serialization)
# ============================================================

class LoginSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=1, max=64))
    password = fields.String(required=True, validate=validate.Length(min=1, max=128))


class RegisterSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=64))
    password = fields.String(required=True, validate=validate.Length(min=6, max=128))
    real_name = fields.String(validate=validate.Length(max=64))
    role = fields.String(load_default="admin", validate=validate.OneOf(["admin", "super_admin"]))


class CategorySchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=64))
    code = fields.String(validate=validate.Length(max=32))
    description = fields.String(validate=validate.Length(max=255))
    created_at = fields.DateTime(dump_only=True)


class ReaderSchema(Schema):
    id = fields.Integer(dump_only=True)
    card_no = fields.String(required=True, validate=validate.Length(min=1, max=32))
    name = fields.String(required=True, validate=validate.Length(min=1, max=64))
    gender = fields.String(validate=validate.OneOf(["male", "female", "other"]))
    phone = fields.String(validate=validate.Length(max=20))
    email = fields.Email(allow_none=True)
    department = fields.String(validate=validate.Length(max=128))
    status = fields.String(load_default="active", validate=validate.OneOf(["active", "disabled"]))
    max_borrow = fields.Integer(load_default=5, validate=validate.Range(min=1, max=100))
    created_at = fields.DateTime(dump_only=True)


class BookSchema(Schema):
    id = fields.Integer(dump_only=True)
    isbn = fields.String(validate=validate.Length(max=32))
    title = fields.String(required=True, validate=validate.Length(min=1, max=255))
    author = fields.String(validate=validate.Length(max=128))
    publisher = fields.String(validate=validate.Length(max=128))
    publish_year = fields.Integer(validate=validate.Range(min=0, max=3000))
    category_id = fields.Integer()
    location = fields.String(validate=validate.Length(max=64))
    total_quantity = fields.Integer(load_default=1, validate=validate.Range(min=0))
    available_quantity = fields.Integer(load_default=1, validate=validate.Range(min=0))
    price = fields.Float(load_default=0.0, validate=validate.Range(min=0))
    description = fields.String()
    cover_url = fields.String(validate=validate.Length(max=500))
    created_at = fields.DateTime(dump_only=True)
    category = fields.Nested(CategorySchema, dump_only=True)

    @validates("category_id")
    def validate_category(self, value):
        if value is not None:
            cat = Category.query.get(value)
            if cat is None:
                raise ValidationError(f"分类ID {value} 不存在")
        return value


class BorrowSchema(Schema):
    id = fields.Integer(dump_only=True)
    reader_id = fields.Integer(required=True)
    book_id = fields.Integer(required=True)
    borrow_date = fields.Date(load_default=date.today)
    due_days = fields.Integer(load_default=30, data_key="due_days", load_only=True,
                              validate=validate.Range(min=1, max=180))
    due_date = fields.Date(dump_only=True)
    return_date = fields.Date(dump_only=True)
    renew_count = fields.Integer(dump_only=True)
    status = fields.String(dump_only=True)
    fine_amount = fields.Float(dump_only=True)
    fine_paid = fields.Boolean(dump_only=True)
    remark = fields.String(validate=validate.Length(max=500))
    reader = fields.Dict(dump_only=True)
    book = fields.Dict(dump_only=True)


class RenewSchema(Schema):
    record_id = fields.Integer(required=True)
    extra_days = fields.Integer(load_default=30, validate=validate.Range(min=1, max=180))


class ReturnSchema(Schema):
    record_id = fields.Integer(required=True)
    remark = fields.String(validate=validate.Length(max=500))

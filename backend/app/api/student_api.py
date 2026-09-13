from datetime import date, timedelta

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, current_user
from marshmallow import ValidationError

from ..extensions import db
from ..models import (
    Reader,
    Book,
    BorrowRecord,
    Reservation,
    StudentLoginSchema,
    StudentReservationSchema,
    ChangePasswordSchema,
    ForgotPasswordSchema,
)
from ..config import Config
from .decorators import reader_required

student_bp = Blueprint("student", __name__)

# 预约保留天数:学生需在此日期前到馆办理
RESERVATION_KEEP_DAYS = 7
# 在借状态:borrowed 正常在借,overdue 表示超期未还,二者均占用借阅名额
ACTIVE_STATUSES = ("borrowed", "overdue")


def _paginate(query):
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(
        max(int(request.args.get("page_size", Config.DEFAULT_PAGE_SIZE)), 1),
        Config.MAX_PAGE_SIZE,
    )
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    return {
        "items": [r.to_dict(include_reader=False) for r in pagination.items],
        "total": pagination.total,
        "page": page,
        "page_size": page_size,
        "pages": pagination.pages,
    }


@student_bp.post("/login")
def student_login():
    """学生登录:借书证号 + 密码,签发带 reader 角色的 JWT"""
    try:
        data = StudentLoginSchema().load(request.get_json(force=True, silent=True) or {})
    except ValidationError as e:
        return jsonify({"code": 400, "msg": "参数校验失败", "errors": e.messages}), 400

    reader = Reader.query.filter_by(card_no=data["card_no"]).first()
    if not reader or not reader.check_password(data["password"]):
        return jsonify({"code": 401, "msg": "借书证号或密码错误"}), 401
    if reader.status != "active":
        return jsonify({"code": 403, "msg": "该账户已被停用,请联系管理员"}), 403

    access_token = create_access_token(
        identity=str(reader.id), additional_claims={"role": "reader"}
    )
    return jsonify({
        "code": 0,
        "msg": "登录成功",
        "data": {
            "access_token": access_token,
            "user": reader.to_dict(),
        },
    })


@student_bp.post("/forgot-password")
def forgot_password():
    """忘记密码:校验借书证号 + 预留手机号,通过后重置密码(无需登录)"""
    try:
        data = ForgotPasswordSchema().load(request.get_json(force=True, silent=True) or {})
    except ValidationError as e:
        return jsonify({"code": 400, "msg": "参数校验失败", "errors": e.messages}), 400

    reader = Reader.query.filter_by(card_no=data["card_no"]).first()
    # 统一错误信息,避免证号枚举:不区分"证号不存在"与"手机号不匹配"
    if not reader or not reader.phone or reader.phone != data["phone"]:
        return jsonify({"code": 400, "msg": "借书证号或预留手机号不正确"}), 400
    if reader.status != "active":
        return jsonify({"code": 403, "msg": "该账户已被停用,请联系管理员"}), 403

    reader.set_password(data["new_password"])
    db.session.commit()
    return jsonify({"code": 0, "msg": "密码重置成功,请使用新密码登录"})


@student_bp.get("/profile")
@reader_required
def student_profile():
    """获取当前学生信息"""
    return jsonify({"code": 0, "msg": "ok", "data": current_user.to_dict()})


@student_bp.put("/password")
@reader_required
def student_change_password():
    """修改本人密码:校验旧密码,新密码不得与旧密码相同"""
    try:
        data = ChangePasswordSchema().load(request.get_json(force=True, silent=True) or {})
    except ValidationError as e:
        return jsonify({"code": 400, "msg": "参数校验失败", "errors": e.messages}), 400

    if not current_user.check_password(data["old_password"]):
        return jsonify({"code": 400, "msg": "原密码错误"}), 400
    if data["old_password"] == data["new_password"]:
        return jsonify({"code": 400, "msg": "新密码不能与原密码相同"}), 400

    current_user.set_password(data["new_password"])
    db.session.commit()
    return jsonify({"code": 0, "msg": "密码修改成功"})


@student_bp.get("/borrows")
@reader_required
def student_borrows():
    """我的借阅记录:强制限定本人,支持 status 过滤 + 分页"""
    q = BorrowRecord.query.filter_by(reader_id=current_user.id)
    q = q.order_by(BorrowRecord.id.desc())

    status = request.args.get("status")
    if status:
        q = q.filter_by(status=status)

    return jsonify({"code": 0, "msg": "ok", "data": _paginate(q)})


@student_bp.get("/borrows/active")
@reader_required
def student_active_borrows():
    """我的在借图书:借阅中 + 逾期未还,供图书页判断按钮状态"""
    recs = (
        BorrowRecord.query.filter(
            BorrowRecord.reader_id == current_user.id,
            BorrowRecord.status.in_(ACTIVE_STATUSES),
        )
        .order_by(BorrowRecord.due_date.asc())
        .all()
    )
    return jsonify({
        "code": 0,
        "msg": "ok",
        "data": {
            "items": [r.to_dict(include_reader=False) for r in recs],
            "count": len(recs),
            "max_borrow": current_user.max_borrow,
        },
    })


@student_bp.get("/reservations")
@reader_required
def student_reservations():
    """我的预约:强制限定本人,支持 status 过滤 + 分页"""
    q = Reservation.query.filter_by(reader_id=current_user.id)
    q = q.order_by(Reservation.id.desc())

    status = request.args.get("status")
    if status:
        q = q.filter_by(status=status)

    return jsonify({"code": 0, "msg": "ok", "data": _paginate(q)})


@student_bp.post("/reservations")
@reader_required
def student_create_reservation():
    """线上预约索书:仅登记预约意向,不扣减库存;到馆由管理员确认后才转为借阅"""
    try:
        data = StudentReservationSchema().load(request.get_json(force=True, silent=True) or {})
    except ValidationError as e:
        return jsonify({"code": 400, "msg": "参数校验失败", "errors": e.messages}), 400

    if current_user.status != "active":
        return jsonify({"code": 403, "msg": "该账户已被停用,请联系管理员"}), 403

    book = Book.query.get(data["book_id"])
    if not book:
        return jsonify({"code": 404, "msg": "图书不存在"}), 404

    # 同一本图书已有预约中记录,不可重复预约
    dup_reserve = Reservation.query.filter_by(
        reader_id=current_user.id, book_id=book.id, status=Reservation.RESERVED
    ).first()
    if dup_reserve:
        return jsonify({"code": 400, "msg": "您已预约该书,请到馆办理或先取消预约"}), 400

    # 同一本图书在借(含逾期未还)不可预约
    dup_borrow = BorrowRecord.query.filter(
        BorrowRecord.reader_id == current_user.id,
        BorrowRecord.book_id == book.id,
        BorrowRecord.status.in_(ACTIVE_STATUSES),
    ).first()
    if dup_borrow:
        return jsonify({"code": 400, "msg": "您已借阅该书且尚未归还,无需重复预约"}), 400

    # 名额:在借 + 预约中 合计不超过 max_borrow
    active_count = BorrowRecord.query.filter(
        BorrowRecord.reader_id == current_user.id,
        BorrowRecord.status.in_(ACTIVE_STATUSES),
    ).count()
    reserve_count = Reservation.query.filter_by(
        reader_id=current_user.id, status=Reservation.RESERVED
    ).count()
    if active_count + reserve_count >= current_user.max_borrow:
        return jsonify(
            {"code": 400, "msg": f"在借与预约合计已达上限({current_user.max_borrow} 本)"}
        ), 400

    reserve_date = date.today()
    rec = Reservation(
        reader_id=current_user.id,
        book_id=book.id,
        status=Reservation.RESERVED,
        reserve_date=reserve_date,
        expire_date=reserve_date + timedelta(days=RESERVATION_KEEP_DAYS),
    )
    # 注意:预约不扣减 available_quantity,库存以实际到馆办理时为准
    db.session.add(rec)
    db.session.commit()
    return jsonify({"code": 0, "msg": "预约成功,请在保留期内到馆办理借书手续",
                    "data": rec.to_dict(include_reader=False)}), 201


@student_bp.post("/reservations/<int:rid>/cancel")
@reader_required
def student_cancel_reservation(rid):
    """取消本人预约:仅预约中可取消"""
    rec = Reservation.query.get_or_404(rid)
    if rec.reader_id != current_user.id:
        return jsonify({"code": 403, "msg": "无权操作该预约"}), 403
    if rec.status != Reservation.RESERVED:
        return jsonify({"code": 400, "msg": "仅预约中的记录可取消"}), 400

    rec.status = Reservation.CANCELLED
    db.session.commit()
    return jsonify({"code": 0, "msg": "预约已取消", "data": rec.to_dict(include_reader=False)})

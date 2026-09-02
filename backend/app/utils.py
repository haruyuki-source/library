from flask import jsonify


def success(data=None, msg: str = "success", code: int = 200):
    """构造成功响应"""
    return jsonify({"code": code, "msg": msg, "data": data}), code


def error(msg: str = "error", code: int = 400, data=None):
    """构造失败响应"""
    return jsonify({"code": code, "msg": msg, "data": data}), code


def paginate(query, page: int, per_page: int, serializer=None):
    """分页查询并返回标准结构

    :param query: SQLAlchemy Query 对象
    :param page: 当前页码
    :param per_page: 每页数量
    :param serializer: 单条数据的序列化函数，缺省使用模型 to_dict()
    """
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    if serializer is None:
        items = [item.to_dict() for item in pagination.items]
    else:
        items = [serializer(item) for item in pagination.items]
    return {
        "items": items,
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
    }

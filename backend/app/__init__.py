from datetime import date
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager

from .config import Config
from .extensions import db, migrate, jwt, cors
from .models import Admin, Category, Book, Reader, BorrowRecord  # noqa: F401 - 确保模型被注册


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources=app.config.get("CORS_RESOURCES", {r"/api/*": {"origins": "*"}}))

    # JWT: 从 sub (admin id) 加载用户
    @jwt.user_lookup_loader
    def _user_lookup(_jwt_header, jwt_data):
        identity = jwt_data.get("sub")
        if identity is None:
            return None
        return Admin.query.get(int(identity))

    # 注册蓝图（延迟导入避免循环）
    from .api.auth_api import auth_bp
    from .api.category_api import category_bp
    from .api.book_api import book_bp
    from .api.reader_api import reader_bp
    from .api.borrow_api import borrow_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(category_bp, url_prefix="/api/categories")
    app.register_blueprint(book_bp, url_prefix="/api/books")
    app.register_blueprint(reader_bp, url_prefix="/api/readers")
    app.register_blueprint(borrow_bp, url_prefix="/api/borrow")

    # 健康检查 & 根路由
    @app.route("/")
    def index():
        return jsonify({
            "app": "Library Management System API",
            "version": "1.0.0",
            "status": "running",
        })

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    # 全局错误处理
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"code": 400, "msg": f"Bad Request: {e.description}"}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"code": 401, "msg": "Unauthorized"}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"code": 403, "msg": "Forbidden"}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"code": 404, "msg": "Resource Not Found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"code": 500, "msg": f"Internal Server Error: {str(e)}"}), 500

    # 初始化数据：建表 + 默认管理员 + 示例分类/图书/读者
    with app.app_context():
        db.create_all()
        _seed_defaults()

    return app


def _seed_defaults() -> None:
    """首次启动时填充示例数据"""
    # 默认管理员
    if Admin.query.count() == 0:
        admin = Admin(username="admin", real_name="超级管理员", role="super_admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.flush()

    # 默认分类
    if Category.query.count() == 0:
        cats = [
            Category(name="计算机科学", code="CS", description="计算机相关书籍"),
            Category(name="文学", code="LIT", description="文学类书籍"),
            Category(name="历史", code="HIS", description="历史类书籍"),
            Category(name="自然科学", code="SCI", description="科学类书籍"),
            Category(name="经济管理", code="ECO", description="经济与管理书籍"),
        ]
        db.session.add_all(cats)
        db.session.flush()

    # 默认读者
    if Reader.query.count() == 0:
        readers = [
            Reader(card_no="R2024001", name="张三", gender="male",
                   phone="13800000001", email="zhangsan@example.com",
                   department="计算机学院"),
            Reader(card_no="R2024002", name="李四", gender="female",
                   phone="13800000002", email="lisi@example.com",
                   department="文学院"),
            Reader(card_no="R2024003", name="王五", gender="male",
                   phone="13800000003", email="wangwu@example.com",
                   department="历史学院"),
        ]
        db.session.add_all(readers)
        db.session.flush()

    # 默认图书
    if Book.query.count() == 0:
        cat_cs = Category.query.filter_by(code="CS").first()
        cat_lit = Category.query.filter_by(code="LIT").first()
        cat_his = Category.query.filter_by(code="HIS").first()
        books = [
            Book(isbn="9787111213826", title="深入理解计算机系统", author="Bryant",
                 publisher="机械工业出版社", publish_year=2016,
                 category_id=cat_cs.id if cat_cs else None,
                 location="A-1-01", total_quantity=3, available_quantity=3,
                 price=139.0, description="CSAPP经典教材"),
            Book(isbn="9787111407010", title="算法导论", author="Cormen",
                 publisher="机械工业出版社", publish_year=2013,
                 category_id=cat_cs.id if cat_cs else None,
                 location="A-1-02", total_quantity=2, available_quantity=2,
                 price=128.0, description="算法领域权威参考书"),
            Book(isbn="9787020024759", title="红楼梦", author="曹雪芹",
                 publisher="人民文学出版社", publish_year=2008,
                 category_id=cat_lit.id if cat_lit else None,
                 location="B-2-05", total_quantity=5, available_quantity=5,
                 price=59.0, description="四大名著之一"),
            Book(isbn="9787108006417", title="万历十五年", author="黄仁宇",
                 publisher="生活·读书·新知三联书店", publish_year=1997,
                 category_id=cat_his.id if cat_his else None,
                 location="C-1-10", total_quantity=3, available_quantity=3,
                 price=28.0, description="历史学名著"),
        ]
        db.session.add_all(books)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

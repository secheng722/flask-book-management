import os
import pymysql
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_database_if_not_exists(app):
    """创建数据库（如果不存在）"""
    try:
        # 解析数据库URL
        db_url = urlparse(app.config['SQLALCHEMY_DATABASE_URI'])
        if db_url.scheme != 'mysql+pymysql':
            # 不是MySQL，无需创建
            return
            
        # 提取连接信息
        db_name = db_url.path.strip('/')
        if not db_name:
            # 没有指定数据库名，无需创建
            return
            
        # 提取用户名、密码、主机和端口
        user = db_url.username or 'root'
        password = db_url.password or ''
        host = db_url.hostname or 'localhost'
        port = db_url.port or 3306
        
        # 创建连接（不指定数据库）
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4'
        )
        
        print(f"尝试创建数据库：{db_name}...")
        
        with conn.cursor() as cursor:
            # 使用utf8mb4字符集创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        conn.close()
        print(f"数据库 {db_name} 已成功创建或已存在")
        
    except Exception as e:
        print(f"创建数据库出错: {str(e)}")
        # 不抛出异常，让应用继续启动（否则陷入循环）


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 尝试创建数据库（如果不存在）
    create_database_if_not_exists(app)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # 配置登录管理器
    login_manager.login_view = "auth.login"
    login_manager.login_message = "请先登录以访问此页面。"
    login_manager.login_message_category = "info"

    # 注册蓝图
    from app.views import auth_bp, book_bp, borrowing_bp, main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(borrowing_bp)

    with app.app_context():
        db.create_all()

        # 创建默认管理员用户
        from app.models import Book, User

        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(username="admin", email="admin@example.com", is_admin=True)
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("创建默认管理员用户: admin/admin123")

        # 创建默认普通用户
        user = User.query.filter_by(username="user").first()
        if not user:
            user = User(username="user", email="user@example.com", is_admin=False)
            user.set_password("user123")
            db.session.add(user)
            db.session.commit()
            print("创建默认普通用户: user/user123")

        # 创建默认示例图书
        if Book.query.count() == 0:
            sample_books = [
                {
                    "title": "红楼梦",
                    "author": "曹雪芹",
                    "isbn": "9787020002207",
                    "publication_year": 1791,
                    "genre": "小说",
                    "description": "中国古典四大名著之一，描述了贾、史、王、薛四大家族的兴衰，以贾宝玉、林黛玉、薛宝钗的爱情婚姻悲剧为主线，展现了封建社会的各种矛盾。",
                    "available": True,
                },
                {
                    "title": "西游记",
                    "author": "吴承恩",
                    "isbn": "9787020002214",
                    "publication_year": 1592,
                    "genre": "小说",
                    "description": "中国古典四大名著之一，讲述了孙悟空、猪八戒、沙僧保护唐僧西天取经的故事，是一部充满奇幻色彩的神话小说。",
                    "available": True,
                },
                {
                    "title": "水浒传",
                    "author": "施耐庵",
                    "isbn": "9787020002221",
                    "publication_year": 1400,
                    "genre": "小说",
                    "description": "中国古典四大名著之一，描写了北宋末年以宋江为首的108位好汉在梁山起义，以及聚义之后接受招安、四处征战的故事。",
                    "available": True,
                },
                {
                    "title": "三国演义",
                    "author": "罗贯中",
                    "isbn": "9787020002238",
                    "publication_year": 1400,
                    "genre": "历史",
                    "description": "中国古典四大名著之一，描述了从东汉末年到西晋初年之间近105年的历史风云，以三国时期的政治和军事斗争为主要描写内容。",
                    "available": True,
                },
                {
                    "title": "平凡的世界",
                    "author": "路遥",
                    "isbn": "9787020069231",
                    "publication_year": 1986,
                    "genre": "小说",
                    "description": "全景式地反映了中国当代城乡社会生活，通过复杂的矛盾纠葛，以孙少平等人为代表，刻画了社会各阶层众多普通人的形象。",
                    "available": True,
                },
                {
                    "title": "活着",
                    "author": "余华",
                    "isbn": "9787506365437",
                    "publication_year": 1993,
                    "genre": "小说",
                    "description": "讲述了一个人一生的故事，这是一个历尽世间沧桑和磨难老人的人生感言，是一幕演绎人生苦难经历的戏剧。",
                    "available": True,
                },
                {
                    "title": "围城",
                    "author": "钱钟书",
                    "isbn": "9787020008735",
                    "publication_year": 1947,
                    "genre": "小说",
                    "description": "一部讽刺小说，被誉为现代中国最有趣的小说。小说以方鸿渐的生活道路为主线，反映了特定历史时期知识分子的生活和心理。",
                    "available": True,
                },
                {
                    "title": "朝花夕拾",
                    "author": "鲁迅",
                    "isbn": "9787020008742",
                    "publication_year": 1928,
                    "genre": "散文",
                    "description": "鲁迅唯一的一本散文集，收录了鲁迅在1926年创作的10篇回忆性散文，记述了作者童年的生活和青年时求学的历程。",
                    "available": True,
                },
                {
                    "title": "边城",
                    "author": "沈从文",
                    "isbn": "9787020008759",
                    "publication_year": 1934,
                    "genre": "小说",
                    "description": "以20世纪30年代川湘交界的边城小镇茶峒为背景，以兼具抒情诗和小品文的优美笔触，描绘了湘西地区特有的风土人情。",
                    "available": True,
                },
                {
                    "title": "骆驼祥子",
                    "author": "老舍",
                    "isbn": "9787020008766",
                    "publication_year": 1939,
                    "genre": "小说",
                    "description": "描述了来自农村的淳朴健壮的祥子，到北平谋生创业，勤劳的祥子怀着发家、奋斗的美好梦想，但却最终被黑暗的暴风雨所吞噬。",
                    "available": False,
                },
                {
                    "title": "人工智能：一种现代方法",
                    "author": "Stuart Russell, Peter Norvig",
                    "isbn": "9787111543367",
                    "publication_year": 2016,
                    "genre": "科技",
                    "description": "人工智能领域的经典教材，全面介绍了人工智能的理论与实践，涵盖了机器学习、知识表示、推理、规划等核心内容。",
                    "available": True,
                },
                {
                    "title": "深度学习",
                    "author": "Ian Goodfellow, Yoshua Bengio, Aaron Courville",
                    "isbn": "9787111575597",
                    "publication_year": 2016,
                    "genre": "科技",
                    "description": "深度学习领域的权威教材，详细介绍了深度学习的数学基础、模型架构和应用实例，是人工智能学习者的必读书籍。",
                    "available": True,
                },
                {
                    "title": "Python编程：从入门到实践",
                    "author": "Eric Matthes",
                    "isbn": "9787115428028",
                    "publication_year": 2016,
                    "genre": "科技",
                    "description": "一本针对所有层次Python读者而作的Python入门书。全书分两部分：第一部分介绍用Python编程所必须了解的基本概念，第二部分将理论付诸实践。",
                    "available": True,
                },
                {
                    "title": "史记",
                    "author": "司马迁",
                    "isbn": "9787101003048",
                    "publication_year": -91,
                    "genre": "历史",
                    "description": '中国历史上第一部纪传体通史，记载了从上古传说中的黄帝时代到汉武帝时期共3000多年的历史，被誉为"史家之绝唱，无韵之离骚"。',
                    "available": True,
                },
                {
                    "title": "万历十五年",
                    "author": "黄仁宇",
                    "isbn": "9787108009982",
                    "publication_year": 1979,
                    "genre": "历史",
                    "description": '以1587年（万历十五年）为切入点，分析中国传统政治文化的症结，开创了"大历史观"的治史方法。',
                    "available": True,
                },
            ]

            for book_data in sample_books:
                book = Book(**book_data)
                db.session.add(book)

            db.session.commit()
            print(f"创建了 {len(sample_books)} 本示例图书")

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User

        return User.query.get(int(user_id))

    return app

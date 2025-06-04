# -*- coding: utf-8 -*-
"""
用户模型
"""

from datetime import datetime

from flask_bcrypt import check_password_hash, generate_password_hash
from flask_login import UserMixin

from app import db


class User(UserMixin, db.Model):
    """用户模型类"""

    __tablename__ = "user"

    # 基本字段
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(60), nullable=False)

    # 权限字段
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    # 时间字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def is_administrator(self):
        """检查是否为管理员"""
        return self.is_admin

    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f"<User {self.username}>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": self.last_login.strftime("%Y-%m-%d %H:%M:%S")
            if self.last_login
            else None,
        }

# -*- coding: utf-8 -*-
"""
图书模型
"""

from datetime import datetime

from app import db


class Book(db.Model):
    """图书模型类"""

    __tablename__ = "book"

    # 基本字段
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, index=True)
    author = db.Column(db.String(100), nullable=False, index=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False, index=True)

    # 出版信息
    publication_year = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(50), nullable=True, index=True)
    description = db.Column(db.Text, nullable=True)

    # 借阅状态字段
    available = db.Column(db.Boolean, default=True, nullable=False, index=True)
    total_copies = db.Column(db.Integer, default=1, nullable=False)
    available_copies = db.Column(db.Integer, default=1, nullable=False)

    # 时间字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @property
    def is_available_for_borrow(self):
        """检查是否可借阅"""
        return self.available_copies > 0

    def borrow(self):
        """借出图书"""
        if self.available_copies > 0:
            self.available_copies -= 1
            self.available = self.available_copies > 0
            self.updated_at = datetime.utcnow()
            return True
        return False

    def return_book(self):
        """归还图书"""
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            self.available = True
            self.updated_at = datetime.utcnow()
            return True
        return False

    @classmethod
    def search_books(cls, query_text):
        """搜索图书"""
        return cls.query.filter(
            (cls.title.contains(query_text))
            | (cls.author.contains(query_text))
            | (cls.isbn.contains(query_text))
        ).all()

    @classmethod
    def get_books_by_genre(cls, genre):
        """按类型获取图书"""
        return cls.query.filter_by(genre=genre).all()

    def toggle_availability(self):
        """切换可借阅状态（仅管理员）"""
        self.available = not self.available
        self.updated_at = datetime.utcnow()
        return self.available

    def __repr__(self):
        return f"<Book {self.title}>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "publication_year": self.publication_year,
            "genre": self.genre,
            "description": self.description,
            "available": self.available,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies,
            "is_available_for_borrow": self.is_available_for_borrow,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            if self.updated_at
            else None,
        }

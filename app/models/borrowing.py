# -*- coding: utf-8 -*-
"""
借阅记录模型
"""

from datetime import datetime, timedelta

from app import db


class BorrowingRecord(db.Model):
    """借阅记录模型类"""

    __tablename__ = "borrowing_record"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)

    # 借阅时间
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)  # 应还日期
    return_date = db.Column(db.DateTime, nullable=True)  # 实际归还日期

    # 状态
    is_returned = db.Column(db.Boolean, default=False, nullable=False)

    # 关联关系
    user = db.relationship("User", backref=db.backref("borrowing_records", lazy=True))
    book = db.relationship("Book", backref=db.backref("borrowing_records", lazy=True))

    def __init__(self, user_id, book_id, borrow_days=14):
        """初始化借阅记录，默认借阅期14天"""
        self.user_id = user_id
        self.book_id = book_id
        self.borrow_date = datetime.utcnow()
        self.due_date = self.borrow_date + timedelta(days=borrow_days)
        self.is_returned = False

    @property
    def is_overdue(self):
        """检查是否逾期"""
        if self.is_returned:
            return False
        return datetime.utcnow() > self.due_date

    @property
    def days_until_due(self):
        """距离到期还有几天"""
        if self.is_returned:
            return 0
        delta = self.due_date - datetime.utcnow()
        return max(0, delta.days)

    def return_book(self):
        """归还图书"""
        if not self.is_returned:
            self.return_date = datetime.utcnow()
            self.is_returned = True
            # 更新书籍的可借阅数量
            self.book.return_book()
            return True
        return False

    @classmethod
    def get_user_active_borrowings(cls, user_id):
        """获取用户当前借阅的图书"""
        return cls.query.filter_by(user_id=user_id, is_returned=False).all()

    @classmethod
    def get_overdue_borrowings(cls):
        """获取所有逾期的借阅记录"""
        return cls.query.filter(
            cls.is_returned.is_(False), cls.due_date < datetime.utcnow()
        ).all()

    def __repr__(self):
        return f"<BorrowingRecord User:{self.user_id} Book:{self.book_id}>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "book_title": self.book.title if self.book else None,
            "borrow_date": self.borrow_date.strftime("%Y-%m-%d %H:%M:%S"),
            "due_date": self.due_date.strftime("%Y-%m-%d %H:%M:%S"),
            "return_date": self.return_date.strftime("%Y-%m-%d %H:%M:%S")
            if self.return_date
            else None,
            "is_returned": self.is_returned,
            "is_overdue": self.is_overdue,
            "days_until_due": self.days_until_due,
        }

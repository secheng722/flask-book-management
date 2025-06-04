# -*- coding: utf-8 -*-
"""
模型模块初始化
"""

from .book import Book
from .borrowing import BorrowingRecord
from .user import User

__all__ = ["User", "Book", "BorrowingRecord"]

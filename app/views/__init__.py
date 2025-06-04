# -*- coding: utf-8 -*-
"""
视图模块初始化
"""

from .auth_views import auth_bp
from .book_views import book_bp
from .borrowing_views import borrowing_bp
from .main_views import main_bp

__all__ = ["main_bp", "book_bp", "auth_bp", "borrowing_bp"]

# -*- coding: utf-8 -*-
"""
表单模块初始化
"""

from .auth_forms import ChangePasswordForm, LoginForm, RegistrationForm
from .book_forms import BookForm, SearchForm
from .borrowing_forms import BorrowBookForm, ReturnBookForm, SetCopiesForm

__all__ = [
    "BookForm",
    "SearchForm",
    "LoginForm",
    "RegistrationForm",
    "ChangePasswordForm",
    "BorrowBookForm",
    "ReturnBookForm",
    "SetCopiesForm",
]

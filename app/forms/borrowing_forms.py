# -*- coding: utf-8 -*-
"""
借阅相关表单
"""

from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class BorrowBookForm(FlaskForm):
    """借阅图书表单"""

    book_id = IntegerField("图书ID", validators=[DataRequired()])
    submit = SubmitField("借阅图书")


class ReturnBookForm(FlaskForm):
    """归还图书表单"""

    borrowing_id = IntegerField("借阅记录ID", validators=[DataRequired()])
    submit = SubmitField("归还图书")


class SetCopiesForm(FlaskForm):
    """设置图书副本数量表单（仅管理员）"""

    total_copies = IntegerField(
        "总副本数",
        validators=[DataRequired(), NumberRange(min=1, max=100)],
        render_kw={"min": 1, "max": 100},
    )
    submit = SubmitField("更新副本数")

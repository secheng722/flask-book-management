# -*- coding: utf-8 -*-
"""
图书相关表单
"""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)


class BookForm(FlaskForm):
    """图书添加/编辑表单"""

    title = StringField("书名", validators=[DataRequired(), Length(min=1, max=100)])
    author = StringField("作者", validators=[DataRequired(), Length(min=1, max=100)])
    isbn = StringField("ISBN", validators=[DataRequired(), Length(min=10, max=20)])
    publication_year = IntegerField(
        "出版年份", validators=[DataRequired(), NumberRange(min=1000, max=2025)]
    )
    genre = SelectField(
        "类型",
        choices=[
            ("", "请选择类型"),
            ("小说", "小说"),
            ("散文", "散文"),
            ("诗歌", "诗歌"),
            ("科技", "科技"),
            ("历史", "历史"),
            ("传记", "传记"),
            ("教育", "教育"),
            ("其他", "其他"),
        ],
        validators=[Optional()],
    )
    description = TextAreaField("描述", validators=[Optional(), Length(max=500)])
    available = BooleanField("可借阅", default=True)
    submit = SubmitField("提交")

    def __init__(self, original_isbn=None, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        self.original_isbn = original_isbn

    def validate_isbn(self, isbn):
        """验证ISBN是否唯一"""
        if isbn.data != self.original_isbn:
            from app.models import Book

            book = Book.query.filter_by(isbn=isbn.data).first()
            if book:
                raise ValidationError("此ISBN已存在，请使用其他ISBN。")


class SearchForm(FlaskForm):
    """图书搜索表单"""

    search = StringField("搜索", validators=[Optional()])
    genre = SelectField(
        "类型",
        choices=[
            ("", "所有类型"),
            ("小说", "小说"),
            ("散文", "散文"),
            ("诗歌", "诗歌"),
            ("科技", "科技"),
            ("历史", "历史"),
            ("传记", "传记"),
            ("教育", "教育"),
            ("其他", "其他"),
        ],
        validators=[Optional()],
    )
    available_only = BooleanField("仅显示可借阅")
    submit = SubmitField("搜索")

# -*- coding: utf-8 -*-
"""
用户认证相关表单
"""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    StringField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError,
)


class LoginForm(FlaskForm):
    """用户登录表单"""

    username = StringField("用户名", validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField("密码", validators=[DataRequired()])
    remember_me = BooleanField("记住我")
    submit = SubmitField("登录")


class RegistrationForm(FlaskForm):
    """用户注册表单"""

    username = StringField(
        "用户名",
        validators=[
            DataRequired(),
            Length(min=4, max=20, message="用户名长度必须在4-20个字符之间"),
        ],
    )
    email = StringField(
        "邮箱",
        validators=[
            DataRequired(),
            Email(message="请输入有效的邮箱地址"),
        ],
    )
    password = PasswordField(
        "密码",
        validators=[
            DataRequired(),
            Length(min=6, message="密码长度至少6个字符"),
        ],
    )
    password2 = PasswordField(
        "确认密码",
        validators=[
            DataRequired(),
            EqualTo("password", message="两次输入的密码不一致"),
        ],
    )
    submit = SubmitField("注册")

    def validate_username(self, username):
        """验证用户名是否唯一"""
        from app.models import User

        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("用户名已存在，请选择其他用户名。")

    def validate_email(self, email):
        """验证邮箱是否唯一"""
        from app.models import User

        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("邮箱已被注册，请使用其他邮箱。")


class ChangePasswordForm(FlaskForm):
    """修改密码表单"""

    current_password = PasswordField("当前密码", validators=[DataRequired()])
    new_password = PasswordField(
        "新密码",
        validators=[
            DataRequired(),
            Length(min=6, message="密码长度至少6个字符"),
        ],
    )
    new_password2 = PasswordField(
        "确认新密码",
        validators=[
            DataRequired(),
            EqualTo("new_password", message="两次输入的密码不一致"),
        ],
    )
    submit = SubmitField("更新密码")

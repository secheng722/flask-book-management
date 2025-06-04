from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.forms import ChangePasswordForm, LoginForm, RegistrationForm
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()

            next_page = request.args.get("next")
            if not next_page or not next_page.startswith("/"):
                next_page = url_for("main.index")

            flash(f"欢迎回来，{user.username}！", "success")
            return redirect(next_page)
        else:
            flash("用户名或密码错误", "error")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """用户注册"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)

        try:
            db.session.add(user)
            db.session.commit()
            flash("注册成功！请登录您的账户。", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash("注册失败，请稍后再试。", "error")

    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """用户退出"""
    username = current_user.username
    logout_user()
    flash(f"再见，{username}！", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/profile")
@login_required
def profile():
    """用户资料"""
    return render_template("auth/profile.html")


@auth_bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """修改密码"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("密码修改成功！", "success")
            return redirect(url_for("auth.profile"))
        else:
            flash("当前密码错误", "error")

    return render_template("auth/change_password.html", form=form)


@auth_bp.route("/admin/users")
@login_required
def admin_users():
    """管理员用户管理页面"""
    if not current_user.is_admin:
        flash("权限不足，仅管理员可访问。", "error")
        return redirect(url_for("main.index"))

    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("auth/admin_users.html", users=users)


@auth_bp.route("/admin/toggle_admin/<int:user_id>")
@login_required
def toggle_admin(user_id):
    """切换用户管理员状态"""
    if not current_user.is_admin:
        flash("权限不足，仅管理员可执行此操作。", "error")
        return redirect(url_for("main.index"))

    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("不能修改自己的管理员状态。", "error")
        return redirect(url_for("auth.admin_users"))

    user.is_admin = not user.is_admin
    db.session.commit()

    status = "管理员" if user.is_admin else "普通用户"
    flash(f"用户 {user.username} 已设置为{status}。", "success")
    return redirect(url_for("auth.admin_users"))

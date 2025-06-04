# -*- coding: utf-8 -*-
"""
借阅管理视图
"""

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.forms import BorrowBookForm, ReturnBookForm, SetCopiesForm
from app.models import Book, BorrowingRecord

borrowing_bp = Blueprint("borrowing", __name__)


@borrowing_bp.route("/borrow/<int:book_id>", methods=["GET", "POST"])
@login_required
def borrow_book(book_id):
    """借阅图书"""
    book = Book.query.get_or_404(book_id)

    if not book.is_available_for_borrow:
        flash("该图书暂无可借阅副本", "warning")
        return redirect(url_for("book.book_detail", id=book_id))

    # 检查用户是否已经借阅了这本书
    existing_borrow = BorrowingRecord.query.filter_by(
        user_id=current_user.id, book_id=book_id, is_returned=False
    ).first()

    if existing_borrow:
        flash("您已经借阅了这本书", "warning")
        return redirect(url_for("book.book_detail", id=book_id))

    if request.method == "POST":
        # 执行借阅
        if book.borrow():
            # 创建借阅记录
            borrowing_record = BorrowingRecord(user_id=current_user.id, book_id=book_id)
            db.session.add(borrowing_record)
            db.session.commit()
            flash(f"成功借阅《{book.title}》", "success")
        else:
            flash("借阅失败，图书暂无可借阅副本", "error")

        return redirect(url_for("book.book_detail", id=book_id))

    return render_template("borrowing/confirm_borrow.html", book=book)


@borrowing_bp.route("/return/<int:borrowing_id>", methods=["POST"])
@login_required
def return_book(borrowing_id):
    """归还图书"""
    borrowing_record = BorrowingRecord.query.get_or_404(borrowing_id)

    # 检查是否是本人的借阅记录
    if borrowing_record.user_id != current_user.id:
        flash("无权限操作他人的借阅记录", "error")
        return redirect(url_for("borrowing.my_borrowings"))

    if borrowing_record.is_returned:
        flash("该图书已经归还", "warning")
        return redirect(url_for("borrowing.my_borrowings"))

    # 执行归还
    if borrowing_record.return_book():
        db.session.commit()
        flash(f"成功归还《{borrowing_record.book.title}》", "success")
    else:
        flash("归还失败", "error")

    return redirect(url_for("borrowing.my_borrowings"))


@borrowing_bp.route("/my-borrowings")
@login_required
def my_borrowings():
    """我的借阅记录"""
    page = request.args.get("page", 1, type=int)
    per_page = 10

    # 获取当前借阅的图书
    active_borrowings = BorrowingRecord.get_user_active_borrowings(current_user.id)

    # 获取历史借阅记录（分页）
    history_pagination = (
        BorrowingRecord.query.filter_by(user_id=current_user.id, is_returned=True)
        .order_by(BorrowingRecord.return_date.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return render_template(
        "borrowing/my_borrowings.html",
        active_borrowings=active_borrowings,
        history_pagination=history_pagination,
    )


@borrowing_bp.route("/admin/borrowings")
@login_required
def admin_borrowings():
    """管理员查看所有借阅记录"""
    if not current_user.is_admin:
        flash("无权限访问", "error")
        return redirect(url_for("main.index"))

    page = request.args.get("page", 1, type=int)
    per_page = 20

    # 获取当前借阅的图书
    active_borrowings = BorrowingRecord.query.filter_by(is_returned=False).all()

    # 获取逾期的借阅记录
    overdue_borrowings = BorrowingRecord.get_overdue_borrowings()

    # 获取所有借阅记录（分页）
    all_pagination = BorrowingRecord.query.order_by(
        BorrowingRecord.borrow_date.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        "borrowing/admin_borrowings.html",
        active_borrowings=active_borrowings,
        overdue_borrowings=overdue_borrowings,
        all_pagination=all_pagination,
    )


@borrowing_bp.route("/admin/set-copies/<int:book_id>", methods=["GET", "POST"])
@login_required
def set_copies(book_id):
    """设置图书副本数量（仅管理员）"""
    if not current_user.is_admin:
        flash("无权限访问", "error")
        return redirect(url_for("main.index"))

    book = Book.query.get_or_404(book_id)
    form = SetCopiesForm()

    if form.validate_on_submit():
        new_total = form.total_copies.data
        current_borrowed = book.total_copies - book.available_copies

        if new_total < current_borrowed:
            flash(f"副本数不能少于已借出数量({current_borrowed})", "error")
        else:
            book.total_copies = new_total
            book.available_copies = new_total - current_borrowed
            book.available = book.available_copies > 0
            db.session.commit()
            flash(f"已更新《{book.title}》的副本数为{new_total}", "success")
            return redirect(url_for("book.book_detail", id=book_id))

    # 预填充当前副本数
    if request.method == "GET":
        form.total_copies.data = book.total_copies

    return render_template("borrowing/set_copies.html", book=book, form=form)

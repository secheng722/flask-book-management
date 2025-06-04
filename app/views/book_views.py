# -*- coding: utf-8 -*-
"""
图书相关视图
"""

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.forms import BookForm, SearchForm
from app.models import Book

book_bp = Blueprint("book", __name__)


@book_bp.route("/books")
def list_books():
    """图书列表页"""
    form = SearchForm()
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "", type=str)
    genre = request.args.get("genre", "", type=str)
    # 正确处理 available_only 参数
    available_only = request.args.get("available_only") == "true"

    query = Book.query

    if search:
        query = query.filter(
            (Book.title.contains(search))
            | (Book.author.contains(search))
            | (Book.isbn.contains(search))
        )

    if genre:
        query = query.filter(Book.genre == genre)

    if available_only:
        query = query.filter(Book.available.is_(True))

    # 分页
    books = query.order_by(Book.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )

    genres = (
        db.session.query(Book.genre).distinct().filter(Book.genre.isnot(None)).all()
    )
    genres = [g[0] for g in genres]

    return render_template(
        "books.html",
        books=books,
        form=form,
        search=search,
        genre=genre,
        genres=genres,
        available_only=available_only,
    )


@book_bp.route("/add_book", methods=["GET", "POST"])
@login_required
def add_book():
    """添加图书页（仅管理员）"""
    if not current_user.is_admin:
        flash("只有管理员可以添加图书", "error")
        return redirect(url_for("book.list_books"))

    form = BookForm()
    if form.validate_on_submit():
        book = Book(
            title=form.title.data,
            author=form.author.data,
            isbn=form.isbn.data,
            publication_year=form.publication_year.data,
            genre=form.genre.data,
            description=form.description.data,
            available=form.available.data,
        )

        try:
            db.session.add(book)
            db.session.commit()
            flash("图书添加成功！", "success")
            return redirect(url_for("book.list_books"))
        except Exception:
            db.session.rollback()
            flash("添加图书时发生错误，请检查ISBN是否重复。", "error")

    return render_template("add_book.html", form=form)


@book_bp.route("/edit_book/<int:id>", methods=["GET", "POST"])
@login_required
def edit_book(id):
    """编辑图书（仅管理员）"""
    if not current_user.is_admin:
        flash("只有管理员可以编辑图书", "error")
        return redirect(url_for("book.book_detail", id=id))

    book = Book.query.get_or_404(id)
    form = BookForm(obj=book)

    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.isbn = form.isbn.data
        book.publication_year = form.publication_year.data
        book.genre = form.genre.data
        book.description = form.description.data
        book.available = form.available.data

        try:
            db.session.commit()
            flash("图书更新成功！", "success")
            return redirect(url_for("book.book_detail", id=book.id))
        except Exception:
            db.session.rollback()
            flash("更新图书时发生错误，请检查ISBN是否重复。", "error")

    return render_template("edit_book.html", form=form, book=book)


@book_bp.route("/book/<int:id>")
def book_detail(id):
    """图书详情页"""
    book = Book.query.get_or_404(id)
    return render_template("book_detail.html", book=book)


@book_bp.route("/delete_book/<int:id>", methods=["DELETE", "POST"])
@login_required
def delete_book(id):
    """删除图书（仅管理员）"""
    if not current_user.is_admin:
        return jsonify({"success": False, "message": "只有管理员可以删除图书"}), 403

    book = Book.query.get_or_404(id)

    # 检查是否有未归还的借阅记录（使用直接查询而不是关系属性）
    from app.models import BorrowingRecord

    active_borrowings_count = BorrowingRecord.query.filter_by(
        book_id=book.id, is_returned=False
    ).count()

    if active_borrowings_count > 0:
        return jsonify(
            {
                "success": False,
                "message": f"该图书有{active_borrowings_count}条未归还的借阅记录，无法删除",
            }
        ), 400

    try:
        # 先删除与图书相关的所有已归还的借阅记录
        all_borrowing_records = BorrowingRecord.query.filter_by(
            book_id=book.id, is_returned=True
        ).all()
        for record in all_borrowing_records:
            db.session.delete(record)

        # 然后再删除图书
        db.session.delete(book)
        db.session.commit()
        return jsonify({"success": True, "message": "图书删除成功"})
    except Exception as e:
        print(f"Error deleting book with ID {id}: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "message": "删除图书时发生错误"}), 500


@book_bp.route("/toggle_availability/<int:id>", methods=["POST"])
@login_required
def toggle_availability(id):
    """切换图书可借阅状态（仅管理员）"""
    if not current_user.is_admin:
        return jsonify({"success": False, "message": "只有管理员可以修改图书状态"}), 403

    book = Book.query.get_or_404(id)

    try:
        new_status = book.toggle_availability()
        db.session.commit()
        return jsonify(
            {
                "success": True,
                "available": new_status,
                "message": f"图书状态已更新为{'可借阅' if new_status else '不可借阅'}",
            }
        )
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "更新状态时发生错误"}), 500

# -*- coding: utf-8 -*-
"""
主页相关视图
"""

from flask import Blueprint, render_template

from app.models import Book

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """首页"""
    total_books = Book.query.count()
    available_books = Book.query.filter_by(available=True).count()
    recent_books = Book.query.order_by(Book.created_at.desc()).limit(5).all()

    return render_template(
        "index.html",
        total_books=total_books,
        available_books=available_books,
        recent_books=recent_books,
    )

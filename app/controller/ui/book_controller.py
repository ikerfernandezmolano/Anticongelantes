from flask import Blueprint, request, redirect, render_template, flash

from app.controller.model.book_controller import BookController


def book_blueprint(db):
    bp = Blueprint('books', __name__)
    service = BookController(db)

    @bp.route('/books', methods=['GET', 'POST'])
    def books():
        if request.method == 'POST':
            try:
                service.create_book(
                    request.form['title'],
                    int(request.form['copies']),
                )
                flash("Usuario creado correctamente", 'success')
            except ValueError as e:
                flash(str(e), "error")
            return redirect('/books')

        return render_template('books.html', books=service.get_all())

    return bp
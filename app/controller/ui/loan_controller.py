from flask import Blueprint, request, redirect, render_template, flash

from app.controller.model.book_controller import BookController
from app.controller.model.loan_controller import LoanController


def loan_blueprint(db):
    bp = Blueprint('loans', __name__)

    loan_service = LoanController(db)
    book_service = BookController(db)

    @bp.route('/loans', methods=['GET', 'POST'])
    def loans():
        if request.method == 'POST':
            try:
                loan_service.create_loan(
                    request.form['user_id'],
                    request.form['book_id'],
                )
                flash("Préstamos registrado correctamente", 'success')
            except ValueError as e:
                flash(str(e), "error")
            return redirect('/loans')

        return render_template(
            'loans.html',
            loans=loan_service.get_all(),
            books=book_service.get_all()
        )

    @bp.route('/loans/return/<int:loan_id>', methods=['GET', 'POST'])
    def return_loan(loan_id):
        try:
            loan_service.return_loan(loan_id)
            flash('Préstamo devuelto correctamente', 'success')
        except ValueError as e:
            flash(str(e), "error")
        return redirect('/loans')


    return bp
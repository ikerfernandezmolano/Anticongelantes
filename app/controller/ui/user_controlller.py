from flask import Blueprint, request, redirect, render_template, flash

from app.controller.model.user_controller import UserController


def user_blueprint(db):
    bp = Blueprint('users', __name__)
    service = UserController(db)

    @bp.route('/users', methods=['GET', 'POST'])
    def users():
        if request.method == 'POST':
            try:
                service.create_user(request.form['name'])
                flash("Usuario creado correctamente")
            except ValueError as e:
                flash(str(e), "error")
            return redirect('/users')

        return render_template('users.html', users=service.get_all())

    return bp
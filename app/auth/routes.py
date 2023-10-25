from app import db, create_app
from app.models import User
from app.auth.forms import LoginForm, RegisterForm, ResetPasswordRequestForm, ResetPasswordForm
from app.auth.email import sendPasswordResetEmail
from flask import render_template, flash, redirect, request, url_for, g
from flask_login import current_user, login_user, logout_user
from flask_babel import _, get_locale
from datetime import datetime

from app.auth import bp as auth_bp


@auth_bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect("/")
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_("Invalid username or password"))
            return redirect("/login")
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        return redirect(next_page)
    return render_template("auth/login.html", title="Sing In", form=form)

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if current_user.is_authenticated:
        return redirect("/")
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_("Congratulations, you are now a registered user!"))
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", title="Registration", form=form)

@auth_bp.route("/reset_password_request", methods=["GET", "POST"])
def resetPasswordRequest():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            sendPasswordResetEmail(user)
        flash(_("Check your email for the instructions to reset your password"))
        return redirect(url_for("auth.login"))
    return render_template("auth/request_password_reset.html", title="Reset Password", form=form)

@auth_bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("main.home"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_("Your password has been reset"))
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)
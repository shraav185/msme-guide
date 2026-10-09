import re

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .models import Business, Feedback, User

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("views.home"))
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            flash("Logged in successfully.", "success")
            return redirect(request.args.get("next") or url_for("views.home"))
        flash("Email or password is incorrect.", "error")
    return render_template("login.html", user=current_user)


@auth.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("views.home"))


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for("views.home"))
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        first_name = (request.form.get("first_name") or request.form.get("firstName") or "").strip()
        password1 = request.form.get("password1") or ""
        password2 = request.form.get("password2") or ""

        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            flash("Enter a valid email address.", "error")
        elif len(first_name) < 2:
            flash("First name must be at least 2 characters.", "error")
        elif User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
        elif len(password1) < 8:
            flash("Password must be at least 8 characters.", "error")
        elif password1 != password2:
            flash("Passwords do not match.", "error")
        else:
            user = User(email=email, first_name=first_name, password=generate_password_hash(password1))
            db.session.add(user)
            try:
                db.session.commit()
                login_user(user, remember=True)
                flash("Account created successfully.", "success")
                return redirect(url_for("views.home"))
            except SQLAlchemyError:
                db.session.rollback()
                current_app.logger.exception("Could not create account")
                flash("We could not create your account. Please try again.", "error")
    return render_template("sign_up.html", user=current_user)


@auth.route("/register-btn", methods=["GET", "POST"])
@login_required
def register_btn():
    if request.method == "POST":
        fields = {
            "business_name": "business-name", "business_type": "business-type", "industry": "industry",
            "gst_number": "gst-number", "business_description": "business-description",
            "contact_name": "contact-name", "email": "email", "phone": "phone", "website": "website",
            "street": "street", "city": "city", "state": "state", "postal": "postal", "country": "country",
        }
        values = {field: (request.form.get(form_name) or "").strip() or None for field, form_name in fields.items()}
        required = ("business_name", "business_type", "industry", "contact_name", "email", "phone", "street", "city", "state", "postal", "country")
        if any(not values[field] for field in required):
            flash("Please complete all required business and contact fields.", "error")
        elif not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", values["email"]):
            flash("Enter a valid contact email address.", "error")
        elif not re.fullmatch(r"\+?[0-9\s()\-]{8,20}", values["phone"]):
            flash("Enter a valid phone number.", "error")
        elif not request.form.get("terms"):
            flash("Please accept the terms to continue.", "error")
        else:
            if values["website"] and not values["website"].startswith(("http://", "https://")):
                values["website"] = "https://" + values["website"]
            business = Business(**values, user_id=current_user.id)
            db.session.add(business)
            try:
                db.session.commit()
                flash("Business registered successfully.", "success")
                return redirect(url_for("auth.registration_success", business_id=business.id))
            except SQLAlchemyError:
                db.session.rollback()
                current_app.logger.exception("Could not register business")
                flash("We could not save your registration. Please try again.", "error")
    return render_template("register_btn.html", user=current_user)


@auth.route("/registration-success/<int:business_id>")
@login_required
def registration_success(business_id):
    business = db.session.get(Business, business_id)
    if business is None or business.user_id != current_user.id:
        abort(404)
    return render_template("submit_btn.html", user=current_user, business=business)


PAGE_TEMPLATES = {
    "msme_management": "msme_management.html", "events": "events.html",
    "msme_sambandh": "msme_sambhand.html", "msme_champion": "msme_champion.html",
    "samadhaan": "samadhan.html", "pmegp": "pmegp.html", "my_msme": "my_msme.html",
    "udyam_registration": "udyam_registration.html", "performance_smartboard": "performance_smartboard.html",
    "grievance_monitoring": "grievance_monitoring.html", "champions_portal": "champions_portal.html",
    "about": "about_us.html", "whats_msme": "whats_msme.html", "schemes": "schemes.html",
    "vacancies": "vacancies.html",
}


def _page(template):
    return render_template(template, user=current_user)


for endpoint, template in PAGE_TEMPLATES.items():
    auth.add_url_rule(
        {"msme_sambandh": "/msme-sambhand", "samadhaan": "/samadhaan", "about": "/about-us", "whats_msme": "/whats-msme"}.get(endpoint, "/" + endpoint.replace("_", "-")),
        endpoint=endpoint,
        view_func=lambda template=template: _page(template),
    )


@auth.route("/quick-links")
def quick_links():
    return _page("quick_links.html")


@auth.route("/contact-us", methods=["GET", "POST"])
def contact_us():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        message = (request.form.get("message") or "").strip()
        if len(name) < 2 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) or not message:
            flash("Please provide your name, a valid email address, and feedback.", "error")
        else:
            db.session.add(Feedback(name=name, email=email, message=message))
            try:
                db.session.commit()
                flash("Thank you. Your feedback has been received.", "success")
            except SQLAlchemyError:
                db.session.rollback()
                current_app.logger.exception("Could not save feedback")
                flash("We could not save your feedback. Please try again.", "error")
        return redirect(url_for("auth.contact_us"))
    return _page("contact_us.html")

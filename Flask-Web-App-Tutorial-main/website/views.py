from flask import Blueprint
from flask import render_template
from flask_login import current_user

views = Blueprint('views', __name__)


@views.route('/health')
def health():
    return {"status": "ok"}, 200


@views.route('/', methods=['GET'])
def home():
    return render_template("home.html", user=current_user)
    

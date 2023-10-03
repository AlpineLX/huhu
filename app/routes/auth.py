from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.models.user import db, User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        # 用户存在并且密码正确
        if user and user.check_password(password):
            session['user_id'] = user.id
            return jsonify(success=True)

        # 用户名不存在，进行注册
        elif not user:
            new_user = User(username=username)
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            return jsonify(success=True, reason="registration")

        # 用户名存在，但密码错误
        else:
            return jsonify(success=False, reason="password")

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if not user:
            new_user = User(username=username)
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            return jsonify(success=True, reason="registration")
        else:
            return jsonify(success=False, reason="username_exists")


@auth_bp.route('/homepage', methods=['GET'])
def homepage():
    return render_template('homepage.html')

@auth_bp.route('/logout', methods=['POST'])
def logout():
    if 'user_id' in session:
        session.pop('user_id')
        return jsonify(success=True)
    return jsonify(success=False, message="Not logged in.")

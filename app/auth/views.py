# from flask import render_template, session, flash, redirect, url_for
# from flask_login import login_user, login_required, logout_user
#
# from werkzeug.security import generate_password_hash
#
# from app.forms import loginForm
# from app.models import UserData, UserModel
# from app.firestore_service import get_user, put_user
#
# from . import auth
#
#
# @auth.route('/login', methods=['GET', 'POST'])
# def login():
#     login_form = loginForm()
#     context = {
#         'login_form': login_form,
#     }
#
#     if login_form.validate_on_submit():
#         username = login_form.username.data
#         password = login_form.password.data
#
#         user_document = get_user(username)
#
#         if user_document.to_dict() is not None:
#             password_db = user_document.to_dict().get('password')
#
#             if password_db == password:
#                 user_data = UserData(username, password)
#                 user_model = UserModel(user_data)
#
#                 login_user(user_model)
#
#                 flash('Bienvenido de nuevo')
#
#                 redirect((url_for('hello')))
#
#             else:
#                 flash('La contraseña es incorrecta')
#         else:
#             flash('El usuario es incorrecto')
#
#         #session['username'] = username
#         #flash('Registro exitoso')
#
#         return redirect(url_for('index'))
#
#     return render_template('login.html',**context)
#
# @auth.route('/signup', methods=['GET', 'POST'])
# def signup():
#     signup_form = loginForm()
#     context = {
#         'signup_form': signup_form,
#     }
#
#     if signup_form.validate_on_submit():
#         username = signup_form.username.data
#         password = signup_form.password.data
#         print(signup_form.submit.data)
#
#         user_document = get_user(username)
#
#         if user_document.to_dict() is None:
#             password_hash = generate_password_hash(password)
#             #password_db = user_document.to_dict().get('password')
#             user_data = UserData(username, password_hash)
#             put_user(user_data)
#             user_model = UserModel(user_data)
#             login_user(user_model)
#
#             flash('Bienvenido !!!')
#             redirect((url_for('hello')))
#         else:
#             flash('El usuario ya existe !')
#
#         #session['username'] = username
#         #flash('Registro exitoso')
#
#         return redirect(url_for('index'))
#
#     return render_template('signup.html',**context)
#
# @auth.route('logout')
# @login_required
# def logout():
#     logout_user()
#     flash('Vuelve pronto')
#
#     return redirect(url_for('auth.login'))
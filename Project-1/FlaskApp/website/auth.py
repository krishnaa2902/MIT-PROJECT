from flask import Blueprint,render_template,request,flash,redirect,url_for
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

@auth.route("/login",methods=['GET','POST'],endpoint='login')
def login():
    
    
    if request.method == 'POST':
        email=request.form.get('email')
        password=request.form.get('pass')
        
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password,password):
                flash("Logged in successfully!",category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash("Incorrect password",category='error')
        else:
            flash("Email does not exist",category='error')
    
    return render_template('login.html',user=current_user)

@auth.route("/signup", methods=['GET','POST'],endpoint='signup')
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        num = request.form.get('num')
        password = request.form.get('pass')
        password2 = request.form.get('pass2')

        user = User.query.filter_by(email=email).first()

        if user:
            flash("Email already exists", category='error')
        elif name == None or email == None or num == None or password == None and password2 == None:
            pass
        elif len(num) != 10:
            flash("Invalid number",category='error')
        elif password != password2:
            flash("Password mismatch",category='error')
        else:
            new_user = User(name=name, email=email, password=generate_password_hash(password, method='scrypt'))
            db.session.add(new_user)
            db.session.commit()
            flash("account created",category='success')
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))
    return render_template('signup.html',user=current_user)

@auth.route("/logout",methods=['GET','POST'] ,endpoint='logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


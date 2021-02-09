from __future__ import print_function
import sys

from flask import Flask,flash,render_template,url_for,request,redirect,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from sqlalchemy import asc, desc
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__) #Indexing root folder
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False;
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' # os.environ.get('DATABASE_URL') #sqlite:///test.db' # 3 forward slashes means relative path; 4 forward slashes means exact path
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'VeryVerySecretKey' #os.environ.get('SECRET_KEY')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin'

class Applicants(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200),nullable=False)
	address = db.Column(db.String(200), nullable=False)
	phone = db.Column(db.Integer, nullable=False)
	gender = db.Column(db.String(200), nullable=False)
	date_created = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return '<applicant %r>' % self.id

class Admin(UserMixin, db.Model):
	id=db.Column(db.Integer, primary_key=True)
	username=db.Column(db.String(15),unique=True)
	email=db.Column(db.String(80),unique=True)
	password=db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
	return Admin.query.get((user_id))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/', methods=['POST','GET'])
def index():
	return render_template('index.html')

	if __name__ == "main":
		app.run(debug=True)

@app.route('/infographics', methods=['POST','GET'])
def infographics():
	return render_template('infographics.html')

@app.route('/registration', methods=['POST','GET'])
def registration():
	if request.method == 'POST':
		applicant_name=request.form['name']
		applicant_address=request.form['address']
		applicant_phone=request.form['phone']
		applicant_gender=request.form['gender']
		new_applicant=Applicants(name=applicant_name,address=applicant_address,phone=applicant_phone,gender=applicant_gender)
		try:
			db.session.add(new_applicant)
			db.session.commit()
			return redirect(url_for('registration'))
		except:
			return 'There was some error uploading the application.'
	return render_template('registration.html')

class LoginForm(FlaskForm):
	username = StringField('username', validators=[InputRequired()])
	password = PasswordField('password', validators=[InputRequired()])

@app.route('/admin',methods=['POST','GET'])
def admin():
	if current_user.is_authenticated:
		return redirect(url_for('dashboard'))
		flash('You are already logged in my dude')
	form = LoginForm()
	if form.validate_on_submit():
		user = Admin.query.filter_by(username=form.username.data).first()
		if user:
			if user.password == form.password.data:
				login_user(user,remember=False)
				return redirect(url_for('dashboard'))
			else:
				return '<h1>Wrong Password</h1>'
		else:
			return '<h1>Username or password is invalid.</h1>'
	return render_template('admin.html', form = form)

@app.route('/admin/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
	applicants_count = Applicants.query.count()
	applicants = Applicants.query.order_by(Applicants.id.asc()).all()
	return render_template('admin_dashboard.html',applicants=applicants, applicants_count=applicants_count)

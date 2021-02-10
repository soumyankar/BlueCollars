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

login_manager2 = LoginManager()
login_manager2.init_app(app)
login_manager2.login_view = 'applicantlogin'

class Jobs(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	post=db.Column(db.String(200), nullable=False)
	organization=db.Column(db.String(200), nullable=False)
	salary=db.Column(db.Integer, nullable=False)
	location=db.Column(db.String(200), nullable=False)
	description=db.Column(db.String(200),nullable=False)
	category=db.Column(db.String(200),nullable=False)

	def __repr__(self):
		return '<Job %r>' % self.id

class Applicants(UserMixin, db.Model):
	id=db.Column(db.Integer, primary_key=True)
	username=db.Column(db.String(15),unique=True)
	password=db.Column(db.String(80))
	name = db.Column(db.String(200),nullable=False)
	address = db.Column(db.String(200), nullable=False)
	phone = db.Column(db.Integer, nullable=False)
	gender = db.Column(db.String(200), nullable=False)	
	date_created = db.Column(db.DateTime, default=datetime.utcnow)

class Applications(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	applicant_id=db.Column(db.Integer, nullable=False)
	job_id=db.Column(db.Integer, nullable=False)

class Admin(UserMixin, db.Model):
	id=db.Column(db.Integer, primary_key=True)
	username=db.Column(db.String(15),unique=True)
	email=db.Column(db.String(80),unique=True)
	password=db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
	return Admin.query.get((user_id))

@login_manager2.user_loader
def load_user2(user_id):
	return Applicants.query.get((user_id))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/applicantlogout")
@login_required
def logout2():
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

@app.route('/jobfinding', methods=['POST','GET'])
def jobfinding():
	return render_template('job_finding.html')

@app.route('/jobs', methods=['POST','GET'])
@login_required
def jobs():
	jobs = Jobs.query.all()
	cooks = Jobs.query.filter_by(category='Cooks').count()
	sales = Jobs.query.filter_by(category='Sales').count()
	deliveryman = Jobs.query.filter_by(category='Deliverman').count()
	drivers = Jobs.query.filter_by(category='Drivers').count()
	tailoring = Jobs.query.filter_by(category='Tailoring').count()
	accounting = Jobs.query.filter_by(category='Accounting').count()
	construction = Jobs.query.filter_by(category='Construction').count()
	mining = Jobs.query.filter_by(category='Mining').count()
	attendant = Jobs.query.filter_by(category='Attendant').count()
	return render_template('jobs.html', cooks = cooks, sales = sales, deliveryman = deliveryman, drivers = drivers, tailoring= tailoring, accounting=accounting, construction=construction,mining=mining,attendant=attendant)

@app.route('/registration', methods=['POST','GET'])
def registration():
	if request.method == 'POST':
		applicant_name=request.form['name']
		applicant_address=request.form['address']
		applicant_phone=request.form['phone']
		applicant_gender=request.form['gender']
		applicant_username=request.form['username']
		applicant_password=request.form['password']
		new_applicant=Applicants(name=applicant_name,address=applicant_address,phone=applicant_phone,gender=applicant_gender,username=applicant_username,password=applicant_password)
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
		flash('You are already logged in')
	form = LoginForm()
	if form.validate_on_submit():
		user = Admin.query.filter_by(username=form.username.data).first()
		print (user)
		if user:
			if user.password == form.password.data:
				login_user(user,remember=False)
				return redirect(url_for('dashboard'))
			else:
				return '<h1>Wrong Password</h1>'
		else:
			return '<h1>Username or password is invalid.</h1>'
	return render_template('admin.html', form = form)

@app.route('/applicantlogin', methods=['POST','GET'])
def applicantlogin():
	if current_user.is_authenticated:
		return redirect(url_for('applicantdashboard'))
		flask.flash('You are already logged in')
	form = LoginForm()
	if form.validate_on_submit():
		user = Applicants.query.filter_by(username=form.username.data).first()
		if user:
			if user.password == form.password.data:
				login_user(user,remember=False)
				return redirect(url_for('applicantdashboard'))
			else:
				return '<h1>Wrong Password</h1>'
		else:
			return '<h1>Username or password is invalid.</h1>'
	return render_template('applicant_login.html', form = form)


@app.route('/applicant/dashboard', methods=['GET','POST'])
@login_required
def applicantdashboard():
	applicant = current_user
	return render_template('applicant_dashboard.html',applicant=applicant)

@app.route('/admin/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
	applicants_count = Applicants.query.count()
	applicants = Applicants.query.order_by(Applicants.id.asc()).all()
	return render_template('admin_dashboard.html',applicants=applicants, applicants_count=applicants_count)

@app.route('/admin/addjob',methods=['GET','POST'])
@login_required
def addjob():
	if request.method == 'POST':
		job_post = request.form['post']
		job_org = request.form['organization']
		job_salary = request.form['salary']
		job_description = request.form['description']
		job_category = request.form['category']
		job_location = request.form['location']
		new_job=Jobs(post=job_post,organization=job_org,salary=job_salary,description=job_description,category=job_category,location=job_location)
		try:
			db.session.add(new_job)
			db.session.commit()
			return redirect(url_for('addjob'))
		except:
			return 'There was some error uploading the job.'
	return render_template('addjob.html')

@app.route('/applicant/jobs/<string:category>')
@login_required
def job_browse(category):
	if request.method == 'POST':
		job_id = request.submit
		print (job_id)
	jobs = Jobs.query.filter_by(category=category).all()
	return render_template('browse_jobs.html',category=category, jobs = jobs)


@app.route('/applicant/jobs/apply', methods=['POST'])
@login_required
def job_apply():
	applicant_id = request.args.get('applicant')
	job_id = request.args.get('job')
	print(applicant_id)
	print(job_id)
	return redirect



from __future__ import print_function
import sys

from flask import Flask,flash,render_template,url_for,request,redirect,jsonify,send_file,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from sqlalchemy import asc, desc
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os

app = Flask(__name__) #Indexing root folder
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False;
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' # os.environ.get('DATABASE_URL') #sqlite:///test.db' # 3 forward slashes means relative path; 4 forward slashes means exact path
db = SQLAlchemy(app)
UPLOAD_FOLDER = 'static/uploads/displaypictures'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
	wfh=db.Column(db.String(200), nullable=False)
	restart=db.Column(db.String(200), nullable=False)

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
	qualification = db.Column(db.String(200), nullable=False)
	age = db.Column(db.String(200), nullable=False)	
	date_created = db.Column(db.DateTime, default=datetime.utcnow)

class Applications(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	applicant_id=db.Column(db.Integer, nullable=False)
	job_id=db.Column(db.Integer, nullable=False)
	status=db.Column(db.String(200))

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
	cooks = Jobs.query.filter_by(category='Cooks').count()
	sales = Jobs.query.filter_by(category='Sales').count()
	deliveryman = Jobs.query.filter_by(category='Deliverman').count()
	drivers = Jobs.query.filter_by(category='Drivers').count()
	tailoring = Jobs.query.filter_by(category='Tailoring').count()
	accounting = Jobs.query.filter_by(category='Accounting').count()
	construction = Jobs.query.filter_by(category='Construction').count()
	mining = Jobs.query.filter_by(category='Mining').count()
	attendant = Jobs.query.filter_by(category='Attendant').count()
	return render_template('infographics.html',cooks = cooks, sales = sales, deliveryman = deliveryman, drivers = drivers, tailoring= tailoring, accounting=accounting, construction=construction,mining=mining,attendant=attendant)

@app.route('/jobfinding', methods=['POST','GET'])
def jobfinding():
	return render_template('job_finding.html')

@app.route('/jobs', methods=['POST','GET'])
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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/adminregistration', methods=['POST','GET'])
def adminregistration():
	registration_success = False
	if request.method == 'POST':
		admin_username=request.form['username']
		admin_email=request.form['email']
		admin_password=request.form['password']
		new_admin = Admin(username=admin_username, email=admin_email, password=admin_password)
		try:
			db.session.add(new_admin)
			db.session.commit()
			registration_success = True
			return render_template('adminregistration.html', registration_success=registration_success)
		except:
			return 'There was some error uploading the application.'
	return render_template('adminregistration.html', registration_success=registration_success)

@app.route('/registration', methods=['POST','GET'])
def registration():
	registration_success = False
	if request.method == 'POST':
		applicant_name=request.form['name']
		applicant_address=request.form['address']
		applicant_phone=request.form['phone']
		applicant_gender=request.form['gender']
		applicant_qualification=request.form['qualification']
		applicant_age=request.form['age']
		applicant_username=request.form['username']
		applicant_password=request.form['password']
		applicant_picture=request.files['display']
		applicant_resume=request.files['resume']
		dontneed, file_extension = os.path.splitext(applicant_picture.filename)
		applicant_picture.filename=applicant_username+file_extension
		dontneed, file_extension = os.path.splitext(applicant_resume.filename)
		applicant_resume.filename=applicant_username+file_extension
		new_applicant=Applicants(name=applicant_name,address=applicant_address,phone=applicant_phone,gender=applicant_gender,username=applicant_username,password=applicant_password,age=applicant_age,qualification=applicant_qualification)
		try:
			db.session.add(new_applicant)
			db.session.commit()
			filename = secure_filename(applicant_picture.filename)
			applicant_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			filename2 = secure_filename(applicant_resume.filename)
			applicant_resume.save(os.path.join('static/uploads/resumes', filename2))
			registration_success = True
			return render_template('registration.html', registration_success=registration_success)
		except:
			return 'There was some error uploading the application.'
	return render_template('registration.html', registration_success=registration_success)

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
		admin = Admin.query.get(1)
		print (user)
		if user:
			if user.password == form.password.data:
				print('Loggin in..')
				login_user(admin,remember=False)
				return redirect('/admin/dashboard')
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
	jobsapplied = []
	applicant = current_user
	applications = Applications.query.filter_by(applicant_id=applicant.id).all()
	for x in applications:
		jobsapplied.append(Jobs.query.get(x.job_id))
	jobs = Jobs.query.all()
	return render_template('applicant_dashboard.html',applicant=applicant,applications = applications, jobs=jobs)

@app.route('/admin/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
	print ('hello')
	applicants_count = Applicants.query.count()
	applicants = Applicants.query.order_by(Applicants.id.asc()).all()
	return render_template('admin_dashboard.html',applicants=applicants, applicants_count=applicants_count)

@app.route('/admin/applications', methods=['GET','POST'])
@login_required
def applications():
	applications = Applications.query.all()
	jobs = Jobs.query.all()
	applicants = Applicants.query.all()
	return render_template('applications.html', applicants = applicants, jobs = jobs, applications = applications)

@app.route('/admin/applications/statuschange/<int:id>/<string:status>', methods=['GET','POST'])
@login_required
def statuschange(id,status):
	applications = Applications.query.get(id)
	applications.status=status
	print (applications)
	try:
		db.session.commit()
	except:
		return 'Unable to change status'
	return redirect(url_for('applications'))

@app.route('/admin/addjob',methods=['GET','POST'])
@login_required
def addjob():
	totaljobs=Jobs.query.count()
	if request.method == 'POST':
		job_post = request.form['post']
		job_org = request.form['organization']
		job_salary = request.form['salary']
		job_description = request.form['description']
		job_category = request.form['category']
		job_location = request.form['location']
		job_wfh = request.form['wfh']
		job_restart = request.form['CareerRestart']
		new_job=Jobs(post=job_post,organization=job_org,salary=job_salary,description=job_description,category=job_category,location=job_location,wfh=job_wfh,restart=job_restart)
		try:
			db.session.add(new_job)
			db.session.commit()
			return redirect(url_for('addjob'))
		except:
			return 'There was some error uploading the job.'
	return render_template('addjob.html', totaljobs = totaljobs)

@app.route('/applicant/jobs/<string:category>')
def job_browse(category):
	jobs = Jobs.query.filter_by(category=category).all()
	return render_template('browse_jobs.html',category=category, jobs = jobs)

@app.route('/jobsforwomen')
def jobsforwomen():
	jobs = Jobs.query.filter_by(restart='Yes').all()
	return render_template('jobsforwomen.html', jobs = jobs)


@app.route('/applicant/jobs/apply/<int:id>', methods=['POST','GET'])
@login_required
def job_apply(id):
	apply_success=False
	applicant_id = current_user.id
	job_id = id
	Job = Jobs.query.get(id)
	status = 'Under Consideration'
	new_application = Applications(job_id = job_id, applicant_id = applicant_id, status = status)
	jobs = Jobs.query.filter_by(category=Job.category).all()
	try:
		apply_success= True
		db.session.add(new_application)
		db.session.commit()
	except:
		return 'Couldnt upload the application.'
	return render_template('browse_jobs.html',category = Job.category, jobs=jobs,apply_success= apply_success)


@app.route('/applicant/edit/<int:id>', methods=['POST','GET'])
@login_required
def editprofile(id):
	applicant = Applicants.query.get(id)
	registration_success = True
	if request.method == 'POST':
		applicant.name=request.form['name']
		applicant.address=request.form['address']
		applicant.phone=request.form['phone']
		applicant.gender=request.form['gender']
		applicant.qualification=request.form['qualification']
		applicant.age=request.form['age']
		applicant_picture=request.files['display']
		applicant_resume=request.files['resume']
		dontneed, file_extension = os.path.splitext(applicant_picture.filename)
		applicant_picture.filename=applicant.username+file_extension
		dontneed, file_extension = os.path.splitext(applicant_resume.filename)
		applicant_resume.filename=applicant.username+file_extension
		try:
			db.session.commit()
			filename = secure_filename(applicant_picture.filename)
			applicant_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			filename2 = secure_filename(applicant_resume.filename)
			applicant_resume.save(os.path.join('static/uploads/resumes', filename2))
			registration_success = True
			return render_template('editprofile.html', applicant=applicant,registration_success=registration_success)
		
		except:
			return 'Couldnt edit information.'
	return render_template('editprofile.html', applicant=applicant)

@app.route('/download/<path:filename>', methods=['GET', 'POST'])
@login_required
def download(filename):
    uploads = 'static/uploads/resumes/'
    return send_from_directory(directory=uploads, filename=filename)
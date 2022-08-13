from flask import Flask, render_template, request, redirect
from flask import session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import date
import psycopg2

app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/cms'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://lwovcefsafqauf:58aa40d11d6de75096f032da4538fc27279f61f11cb50ce4decce704b25e9909@ec2-52-73-155-171.compute-1.amazonaws.com:5432/debuoogt4kiqmi'


app.config['SECRET_KEY'] = 'secretkey:):)'

db = SQLAlchemy(app)


class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text)
    password = db.Column(db.Text)

class Complaint(db.Model):
    __tablename__ = "complaint"
    id = db.Column(db.Integer, primary_key=True)
    categoryid = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False, default=1)
    name = db.Column(db.Text, nullable=False)
    phone = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    subject = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    compdate = db.Column(db.Date, default=date.today)
    isapproved = db.Column(db.Boolean, default=False)
    approvedate = db.Column(db.Date, nullable=True)
    isrejected = db.Column(db.Boolean, default=False)
    rejecteddate = db.Column(db.Date, nullable=True)
    isprocessed = db.Column(db.Boolean, default=False)
    processdate = db.Column(db.Date, nullable=True)
    isresolved = db.Column(db.Boolean, default=False)
    resoldate = db.Column(db.Date, nullable=True)

class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    descr = db.Column(db.Text, nullable=False)

@app.route("/", methods = ['GET', 'POST'])
def home():

    if (request.method == 'POST'):
        id = request.form.get('search2')

        currcomp = Complaint.query.filter_by(id=id).first()

        if(currcomp):
            return render_template('homepage.html', found=True, currcomp=currcomp, disp=True)
        else:
            return render_template('homepage.html', found=False, disp=True)

    return render_template('homepage.html', found=False, disp=False)

@app.route("/complain", methods = ['GET', 'POST'])
def comp():

    if (request.method == 'POST'):
        category = request.form.get('category')
        name = request.form.get('name')
        subject = request.form.get('subject')
        email = request.form.get('email')
        number = request.form.get('number')
        message = request.form.get('message')

        entry = Complaint(categoryid=int(category), status=1, name= name, subject = subject, email=email, phone = number, description = message)
        db.session.add(entry)
        db.session.commit()

        return render_template('success.html', id=entry.id)

    return render_template('complain.html')


@app.route("/login", methods = ['GET', 'POST'])
def login():
    if "user" in session:
        return redirect('/dashboard')

    if (request.method == 'POST'):
        username = request.form.get('userName')
        password = request.form.get('Password')

        person = Admin.query.filter_by(username=username).first()

        if person:
            if (username == person.username and password == person.password):
                session['user'] = username
                return redirect('/dashboard')

    return render_template('adminlogin.html')



@app.route("/dashboard", methods = ['GET', 'POST'])
def dashboard():
    if "user" not in session:
        return redirect('/login')

    if (request.method == 'POST'):
        searchval = request.form.get('search3')
        search1 = "%{0}%".format(searchval)

        if search1.isnumeric() == True:
            results = Complaint.query.filter(or_(Complaint.name.like(search1),
                                             Complaint.phone.like(search1),
                                             Complaint.email.like(search1),
                                             Complaint.subject.like(search1),
                                             Complaint.id.like(int(search1))
                                             )).all()
        else:
            results = Complaint.query.filter(or_(Complaint.name.like(search1),
                                                 Complaint.phone.like(search1),
                                                 Complaint.email.like(search1),
                                                 Complaint.subject.like(search1)
                                                 )).all()


        return render_template('dashboard.html', complaints=results)

    complaints = Complaint.query.filter_by().all()

    return render_template('dashboard.html',complaints=complaints)



@app.route("/info")
def dashboardinfo():
    if "user" not in session:
        return redirect('/login')

    return render_template('dashboardinfo.html')

@app.route('/logout')
def logout():
   session.pop('user', None)
   return redirect('/login')

@app.route("/update/<string:id>", methods = ['GET', 'POST'])
def update(id):
    if "user" not in session:
        return redirect('/login')

    if (request.method == 'POST'):
        currstatus = int(request.form.get('status'))
        currcomplaint = Complaint.query.filter_by(id=id).first()

        if currstatus==-1:
            currcomplaint.status = currstatus
            currcomplaint.rejecteddate = date.today()
            currcomplaint.isrejected = 1
            db.session.commit()

        if currstatus==2:
            currcomplaint.status = currstatus
            currcomplaint.approvedate = date.today()
            currcomplaint.isapproved = 1
            db.session.commit()

        if currstatus==3:
            currcomplaint.status = currstatus
            currcomplaint.processdate = date.today()
            currcomplaint.isprocessed = 1
            db.session.commit()

        if currstatus==4:
            currcomplaint.status = currstatus
            currcomplaint.resoldate = date.today()
            currcomplaint.isresolved = 1
            db.session.commit()

    currcomplaint = Complaint.query.filter_by(id=id).first()
    category = Category.query.filter_by(id=currcomplaint.categoryid).first()
    category = category.descr
    return render_template('dashboarddetail.html', currcomplaint=currcomplaint, category=category)


if __name__=="__main__":
    #db.create_all()
    app.run()

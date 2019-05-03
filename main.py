from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzhell@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'K1i2m3H4e5i6m7a8n9n0'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blogtitle = db.Column(db.String(120))
    blogbody = db.Column(db.String(240))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blogtitle, blogbody, owner):
        self.blogtitle = blogtitle
        self.blogbody = blogbody
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'index', 'list_blogs', 'signup']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():

    users = User.query.all()
    return render_template("index.html", title="Blog Users", users=users)

@app.route('/blog')
def list_blogs():

    oneblog = request.args.get('id')
    oneuser = request.args.get('user')
    if oneblog:
        blogindi = Blog.query.get(oneblog)
        return render_template("blogindi.html", newpost=blogindi)
    elif oneuser:
        user = User.query.get(oneuser)
        return render_template("singleuser.html", title="Blogs by User", blogs=user.blogs)
    else:
        blogs = Blog.query.all()
        return render_template("bloglist.html", title="Build a Blog", blogs=blogs)
    
@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    
    owner = User.query.filter_by(email=session['email']).first()
    if request.method == 'POST':
        newtitle = request.form['blogtitle']
        newbody = request.form['blogbody']
        if (not newtitle) or (newtitle.strip() == ''):
            flash('Please fill in the title', 'error')
        if (not newbody) or (newbody.strip() == '') :
            flash('Please fill in the body'), 'error'
        if newtitle and newbody:
            newpost = Blog(newtitle, newbody, owner)
            db.session.add(newpost)
            db.session.commit()
            return render_template("blogindi.html", newpost = newpost)
    return render_template("blogadd.html", title="Add a Blog Entry")

@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash('Logged in')
            return redirect('/newpost')
        elif user and user.password != password:
            flash('User password incorrect', 'error')
            return render_template('login.html', title="Login", email=email)
        else:
            flash('User does not exist', 'error')
            return render_template('login.html', title="Login", email=email)
    return render_template('login.html', title="Login")

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        if email == '':
            flash("Email can't be left blank", "error")
            email = ''
        elif ' ' in email:
            flash("Email can't contain spaces", "error")        
            email = ''
        elif (len(email) < 3 or len(email) > 50):
            flash('Email must be between 3 and 50 characters long', 'error')        
            email = ''
        elif email.count('@') != 1 and email.count('.') != 1:
            flash('Email must contain one @ and one .(dot)', 'error')        
            email = ''
        
        if password == '':
            flash("Password can't be left blank", "error")
            password = ''
        elif ' ' in password:
            flash("Password can't contain spaces", "error")        
            password = ''
        elif len(password) < 3 or len(password) > 25:
            flash('Password must be between 3 and 25 characters long', 'error')        
            password = ''
        
        if verify == '':
            flash("Verify can't be left blank", "error")
            verify = ''
        elif ' ' in verify:
            flash("Verify can't contain spaces", "error")        
            verify = ''
        elif len(verify) < 3 or len(verify) > 25:
            flash('Verify must be between 3 and 25 characters long', 'error')        
            verify = ''    
        elif verify != password:
            flash("Verify doesn't match password", "error")
            verify = ''

        if not email or not password or not verify:
            # return redirect('/signup')
            return render_template('signup.html', title="Signup", email=email)
        else:
            existing_user = User.query.filter_by(email=email).first()
            if not existing_user:
                new_user = User(email,password)
                db.session.add(new_user)
                db.session.commit()
                session['email'] = email
                return redirect('/newpost')
            else:
                flash('User already exists', 'error')
                
    return render_template('signup.html', title="Signup")

@app.route('/logout')
def logout():

    del session['email']
    flash('Logged out')
    return redirect('/blog')

if __name__ == '__main__':
    app.run()
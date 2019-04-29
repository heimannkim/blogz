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
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/blog', methods=['POST', 'GET'])
def index():

    blogs = Blog.query.filter_by(owner=owner).all()
    oneblog = request.args.get('id')    
    if not oneblog:
        return render_template("bloglist.html", title="Build a Blog", blogs=blogs)
    else:
        blogindi = Blog.query.get(oneblog)
        return render_template("blogindi.html", blogtitle=blogindi.blogtitle, blogbody=blogindi.blogbody)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    owner = User.query.filter_by(email=session['email']).first()
    if request.method == 'POST':
        titleerror = ''
        bodyerror = '' 
        newtitle = request.form['blogtitle']
        newbody = request.form['blogbody']
        if (not newtitle) or (newtitle.strip() == ''):
            titleerror = "Please fill in the title"
        if (not newbody) or (newbody.strip() == '') :
            bodyerror = "Please fill in the body"
        if (not titleerror) and (not bodyerror):
            newpost = Blog(newtitle, newbody, owner)
            db.session.add(newpost)
            db.session.commit()
            blogindi = Blog.query.get(newpost.id)
            return render_template("blogindi.html", blogtitle=blogindi.blogtitle, blogbody=blogindi.blogbody)
        else:
            return render_template("blogadd.html", title="Add a Blog Entry",
                newtitle=newtitle, titleerror=titleerror, 
                newbody=newbody, bodyerror=bodyerror)
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
        else:
            if user and user.password != password:
                flash('User password incorrect', 'error')
            else:
                flash('User does not exist', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if email == '':
            flash("Email can't be left blank")
            email = ''
        else:
        if ' ' in email:
            email_error = "Email can't contain spaces"        
            email = ''
        else:
            if (len(email) < 5 or len(email) > 50):
                email_error = "Email must be between 5 and 50 characters long"        
                email = ''
            else:
                if email.count('@') != 1 and email.count('.') != 1:
                    email_error = "Email must contain one @ and one .(dot)"        
                    email = ''
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email,password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/newpost')
        else:
            flash('User already exists', 'error')
    return render_template('signup.html')

@app.route('/logout')
def logout():

    del session['email']
    return redirect('blog')

if __name__ == '__main__':
    app.run()
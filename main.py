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
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():

    allowed_routes = ['login', 'index', 'list_blogs', 'signup']
    
    if request.endpoint not in allowed_routes and 'username' not in session:
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
    
    owner_id = User.query.filter_by(username=session['username']).first()
    
    if request.method == 'POST':
        newtitle = request.form['blogtitle']
        newbody = request.form['blogbody']
    
        if (not newtitle) or (newtitle.strip() == ''):
            flash('Please fill in the title', 'error')
    
        if (not newbody) or (newbody.strip() == '') :
            flash('Please fill in the body', 'error')
    
        if newtitle and newbody:
            newpost = Blog(newtitle, newbody, owner_id)
            db.session.add(newpost)
            db.session.commit()
            return render_template("blogindi.html", newpost = newpost)
    
    return render_template("blogadd.html", title="Add a Blog Entry")

@app.route('/login', methods=['POST', 'GET'])
def login():

    if 'username' in session:
        flash('User already logged in', 'error')
        return redirect('/')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash('Logged in', 'error')
            return redirect('/newpost')

        elif user and user.password != password:
            flash('User password incorrect', 'error')
            return render_template('login.html', title="Login", username=username)

        else:
            flash('User does not exist', 'error')
            return render_template('login.html', title="Login", username=username)

    return render_template('login.html', title="Login")

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if 'username' in session:
        flash('User already logged in', 'error')
        return redirect('/')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == '':
            flash("Username can't be left blank", "error")
            username = ''

        elif ' ' in username:
            flash("Username can't contain spaces", "error")        
            username = ''

        elif (len(username) < 3 or len(username) > 50):
            flash('Username must be between 3 and 50 characters long', 'error')        
            username = ''
        
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

        if not username or not password or not verify:
            return render_template('signup.html', title="Signup", username=username)

        else:
            existing_user = User.query.filter_by(username=username).first()

            if not existing_user:
                new_user = User(username,password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')

            else:
                flash('User already exists', 'error')
                
    return render_template('signup.html', title="Signup")

@app.route('/logout')
def logout():

    del session['username']
    flash('Logged out', 'error')
    return redirect('/blog')

if __name__ == '__main__':
    app.run()
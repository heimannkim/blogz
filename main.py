from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:bloghell@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blogtitle = db.Column(db.String(120))
    blogbody = db.Column(db.String(240))

    def __init__(self, blogtitle, blogbody):
        self.blogtitle = blogtitle
        self.blogbody = blogbody

@app.route('/blog', methods=['POST', 'GET'])
def index():
      
    blogs = Blog.query.all()
    return render_template("bloglist.html", title="Build a Blog", blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
        
    if request.method == 'POST':
        newtitle = request.form['blogtitle']
        newbody = request.form['blogbody']
        titleerror = ''
        bodyerror = ''
        if newtitle == '':
            titleerror == "Blog title can't be left blank"
        if newbody == '':
            bodyerror == "Blog body can't be left blank"
        if not titleerror and not bodyerror:
            newpost = Blog(newtitle, newbody)
            db.session.add(newpost)
            db.session.commit()
    return render_template("blogadd.html", title="Add a Blog Entry")    
    
if __name__ == '__main__':
    app.run()
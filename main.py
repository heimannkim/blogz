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
    oneblog = request.args.get('id')    
    if not oneblog:
        return render_template("bloglist.html", title="Build a Blog", blogs=blogs)
    else:
        blogindi = Blog.query.get(oneblog)
        return render_template("blogindi.html", blogtitle=blogindi.blogtitle, blogbody=blogindi.blogbody)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

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
            newpost = Blog(newtitle, newbody)
            db.session.add(newpost)
            db.session.commit()
            blogindi = Blog.query.get(newpost.id)
            return render_template("blogindi.html", blogtitle=blogindi.blogtitle, blogbody=blogindi.blogbody)
        else:
            return render_template("blogadd.html", title="Add a Blog Entry",
                newtitle=newtitle, titleerror=titleerror, 
                newbody=newbody, bodyerror=bodyerror)
    return render_template("blogadd.html", title="Add a Blog Entry")
    
if __name__ == '__main__':
    app.run()
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask, session, g, \
        request, render_template, flash, redirect, url_for, abort

# Configurations
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'admin'
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/flaskr.db'

# Create Flaskr application
app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)

# Define database tables
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)

    def __init__(self, title, body, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

    def __repr__(self):
        return '<Post %r>' % self.title

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', backref=db.backref('replies', lazy='dynamic'))

    def __init__(self, comment, post_id, pub_date=None):
        self.comment = comment
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        self.post_id = post_id

    def __repr__(self):
        return '<Reply %r>' % self.comment

# Create database tables
db.create_all()

@app.route('/')
def show_posts():
    posts = Post.query.all()
    return render_template('show_posts.html', posts=posts)

def show_replies():
    replies = Reply.query.all()
    return render_template('show_posts.html', replies=replies)

# Post a entry
@app.route('/post', methods = ['POST'])
def add_post():
    if not session.get('logged_in'):
        abort(401)
    p = Post(request.form['title'], request.form['text'])
    db.session.add(p)
    db.session.commit()
    flash('New post was successfully added.')
    return redirect(url_for('show_posts'))

# Reply to a post
@app.route('/reply', methods = ['POST'])
def add_reply():
    if not session.get('logged_in'):
        abort(401)
    #post_id = Post('post.id')
    r = Reply(request.form['text'], 'post_id') # can't get post_id
    db.session.add(r)
    db.session.commit()
    flash('New reply was successfully added.')
    return redirect(url_for('show_posts'))

# User login
@app.route('/login', methods = ['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in.')
            return redirect(url_for('show_posts'))
    return render_template('login.html', error = error)

# User logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('login'))

# Run the application
if __name__ == '__main__':
    app.run(debug=True)

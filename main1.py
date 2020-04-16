from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/AayushBlog'
db = SQLAlchemy(app)



class Contacts(db.Model):
    '''sn, name, email, phone, message, date'''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(12),  nullable=False)
    message = db.Column(db.String(120),  nullable=False)
    date = db.Column(db.String(20))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/contact', methods=['GET','POST']) #creating endpoints
def contact():
    if(request.method=='POST'):
        # add entry to the database

        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contacts(name=name, email=email, phone=phone, message=message)
        db.session.add(entry)
        db.session.commit()

    return render_template('contact.html')


@app.route('/about') #creating endpoints
def about():

    return render_template('about.html')

@app.route('/post') #creating endpoints
def post():

    return render_template('post.html')





app.run(debug=True)


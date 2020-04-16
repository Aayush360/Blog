from flask import Flask, render_template, request, session, redirect
from flaskext.mysql import MySQL
import json
from flask_mail import Mail
import os
from werkzeug.utils import secure_filename
import math

with open("config.json") as c:
    params = json.loads(c.read())["params"]

print(params)

local_server = True

app = Flask(__name__)
app.config['UPLOAD_FOLDER']= params['upload_location']
app.secret_key="secret-key"
app.config.update(
    MAIL_SERVER ='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME=params['gmail_user'],
    MAIL_PASSWORD=params['gmail_pass']

)
mail = Mail(app)

if (local_server):

    app.config['MYSQL_DATABASE_HOST']= params['local_host']
    app.config['MYSQL_DATABASE_PORT	']= params['local_port']
    app.config['MYSQL_DATABASE_USER']= 'root'
    app.config['MYSQL_DATABASE_PASSWORD']= 'root123!'
    app.config['MYSQL_DATABASE_DB']= params['local_db']
    app.config['MYSQL_DATABASE_CHARSET']= "utf8"
else:
    app.config['MYSQL_DATABASE_HOST'] = params['prod_host']
    app.config['MYSQL_DATABASE_PORT	'] = params['prod_port']
    app.config['MYSQL_DATABASE_USER'] = 'root'
    app.config['MYSQL_DATABASE_PASSWORD'] = 'root123!'
    app.config['MYSQL_DATABASE_DB'] = params['prod_db']
    app.config['MYSQL_DATABASE_CHARSET'] = "utf8"

mysql = MySQL()
mysql.init_app(app)


@app.route('/')
def home():
    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    #[:params["no_of_post"]]
    last = math.ceil(len(posts)/int(params['no_of_post']))
    page = request.args.get('page')
    if(not str(page).isnumeric()):
        page=1
    page=int(page)
    posts=posts[(page-1)*int(params['no_of_post']):(page-1)*int(params['no_of_post'])+int(params['no_of_post'])]

    if(page==1):
        prev="#"
        next="/?page="+str(page+1)
    elif (page==last):
        next='#'
        prev="/?page="+str(page-1)
    else:
        next="/?page="+str(page+1)
        prev ="/?page="+str(page-1)



    # for x in list(posts):
    #     print(x)
    #     title.append(x[0])
    #
    #     content.append(x[3])
    #     img_file.append(x[4])
    #     date.append(x[5])


    print(posts)

    return render_template('index.html', params=params,  posts=posts, prev=prev, next=next)


@app.route('/dashboard', methods=['GET','POST'])
def login():
    if ('user' in session and session['user']==params['admin_user']):
        cursor = mysql.get_db().cursor()
        cursor.execute("SELECT * FROM posts")
        data = cursor.fetchall()
        print(data)
        return render_template('dashboard.html', params=params, datas=data)

    if request.method =='POST':
        username = request.form.get('uname')
        upass = request.form.get('pass')
        if(username== params["admin_user"] and upass==params["admin_password"]):
            session['user']= username
            cursor = mysql.get_db().cursor()
            cursor.execute("SELECT * FROM posts")
            data = cursor.fetchall()
            print(data)
            return render_template('dashboard.html', params=params, datas= data)

    return render_template('login.html',params=params)


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route('/edit/<string:sno>', methods=['GET','POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_user']):

        if request.method =='POST':
            title= request.form.get('title')
            tagline= request.form.get('tagline')
            slug= request.form.get('slug')
            content= request.form.get('content')
            img_file= request.form.get('imgfile')

            if sno=='0':
                cursor = mysql.get_db().cursor()
                cursor.execute("INSERT INTO posts (title, tagline, slug, content, img_file) VALUES (%s, %s, %s, %s, %s)",
                               (title, tagline, slug, content, img_file))
                mysql.get_db().commit()

            else:
                cursor = mysql.get_db().cursor()
                cursor.execute("SELECT * FROM posts WHERE sn="+sno)
                datas = cursor.fetchall()
                print(datas)

                sql = "UPDATE posts SET title = %s, tagline=%s, slug=%s, content=%s, img_file=%s WHERE sn = %s"
                val = (title, tagline,slug,content,img_file,sno)
                cursor.execute(sql,val)
                mysql.get_db().commit()
                cursor.close()
                return redirect('/edit/'+sno)

        cursor = mysql.get_db().cursor()
        cursor.execute("SELECT * FROM posts WHERE sn="+sno)
        datas = cursor.fetchall()
        print(datas)
        if datas== ():
            return render_template('edit.html', params=params, posts=datas,sno=sno)
        else:
            return render_template('edit.html', params=params, posts=datas[0],sno=sno)




@app.route('/uploader', methods=['GET','POST']) #creating endpoints
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
        if (request.method=='POST'):
            if request.files['file1'].filename == '':
                return render_template('dashboard.html', params=params,msg='Please choose your file')
            else:
                f = request.files['file1']
                print(f)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
                return render_template('dashboard.html',params=params,msg='Success Complete')




@app.route('/delete/<string:sno>', methods=['GET','POST']) #creating endpoints
def delete(sno):
    if ('user' in session and session['user'] == params['admin_user']):

        cursor = mysql.get_db().cursor()
        sql = "DELETE FROM posts WHERE sn= %s"
        data=sno
        print(sql)
        cursor.execute(sql,data)
        mysql.get_db().commit()
        cursor.close()

        return redirect("/dashboard")






@app.route('/contact', methods=['GET','POST']) #creating endpoints
def contact():
    if(request.method=='POST'):
        # add entry to the database

        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        #date = request.form.get('date')

        cursor = mysql.get_db().cursor()
        cursor.execute("INSERT INTO contacts (name, email, phone, message) VALUES (%s, %s, %s, %s)", (name, email, phone, message))
        mysql.get_db().commit()
        mail.send_message('New message from '+name , sender=email, recipients=[params['gmail_user']],
                          body = message+'\n'+phone)
        cursor.close()

    return render_template('contact.html', params=params)

@app.route('/post/<string:post_slug>', methods=['GET']) #creating endpoints
def post_route(post_slug):
    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT slug,title,tagline,content,img_file,date FROM posts")
    data = cursor.fetchall()
    print(data)
    title = []
    content = []
    img_file = []
    date = []

    for x in list(data):
        print(x)
        if x[0] == post_slug:
            new_data = x



        print(title)


    return render_template('post.html', params=params, datas=new_data)

@app.route('/about') #creating endpoints
def about():

    return render_template('about.html', params=params)

@app.route('/post') #creating endpoints
def post():
    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT slug,title,tagline,content,img_file,date FROM posts")
    data = cursor.fetchall()

    for x in list(data):
        new_data = x

    return render_template('post.html', params=params, datas=new_data)

app.run(debug=True)


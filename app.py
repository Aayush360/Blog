from flask import Flask
from flaskext.mysql import MySQL


app = Flask(__name__)

app.config['MYSQL_DATABASE_HOST']= '127.0.0.1'
app.config['MYSQL_DATABASE_PORT	']= 3306
app.config['MYSQL_DATABASE_USER']= 'root'
app.config['MYSQL_DATABASE_PASSWORD']= 'root123!'
app.config['MYSQL_DATABASE_DB']= 'DB_flask'
app.config['MYSQL_DATABASE_CHARSET']= "utf8"


mysql = MySQL()
mysql.init_app(app)



@app.route('/')
def index():
    cursor = mysql.get_db().cursor()
    cursor.execute('''CREATE TABLE example (id INTEGER, name VARCHAR(20) )''')
    return 'done'



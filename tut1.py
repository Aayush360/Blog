from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')

def index():
    return render_template('index.html')

@app.route('/about') #creating endpoints


def yes():
    name='aayush'
    return render_template('about.html', name2=name)

@app.route('/boot') #creating endpoints


def bootstrap():
    name='aayush'
    return render_template('boot.html', name2=name)

app.run(debug=True)


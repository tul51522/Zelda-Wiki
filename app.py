from flask import Flask, request, render_template, session
import random
import string

app = Flask(__name__, template_folder='templates')
app.secret_key = "SOME_KEY"

@app.route('/')
def index():
    return render_template('index.html', message="index")

@app.route('/maps')
def maps():
    return render_template('maps.html')

@app.route('/guides')
def guides():
    return render_template('guides.html')

@app.route('/canon')
def canon():
    return render_template('canon.html')

@app.route('/community')
def community():
    return render_template('community.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
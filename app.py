from flask import Flask, request, render_template, session, redirect, url_for
import random
import string
from flask import Flask, jsonify
from flask_mysqldb import MySQL



app = Flask(__name__, template_folder='templates')
app.secret_key = "SOME_KEY"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'zelda_wiki'

mysql = MySQL()
mysql.init_app(app)

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

@app.route('/newarticle', methods=["GET", "POST"])
def newarticle():
    if request.method == "POST":
       cursor = mysql.connection.cursor()
       article_subject = request.form.get("asubject")
       imageurl = request.form.get("iurl") 
       content = request.form.get("acontent")
       cursor.execute(''' INSERT INTO articles VALUES(%s,%s, %s, 1)''',(article_subject, imageurl, content))
       mysql.connection.commit()
       cursor.close()
       return redirect(url_for('index'))
    else:
        return render_template("newarticle.html")

@app.route('/displayarticle/<name>')
def displayarticle(name):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM articles WHERE articlesubject = %s", (name,))
    articleinfo = cursor.fetchone()
    return render_template('displayarticle.html', info=articleinfo)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
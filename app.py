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

games = [
        'ocarina_of_time',
        'majoras_mask',
        'wind_waker',
        'twilight_princess',
        'skyward_sword',
        'breath_of_the_wild',
        'tears_of_the_kingdom'
    ]

@app.route('/guides')
def guides():
    
    return render_template('guides.html', games=games, selected_game=None)

@app.route('/guides/<name>')
def guides_type(name):
   
    if name not in games:
        name = None
    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT * FROM ARTICLES WHERE ARTICLEINFO = %s AND ARTICLETYPE = %s''',(name, "guide"))
    articles = cursor.fetchall()
    cursor.close()
    return render_template('guides.html', games=games, selected_game=name, articles=articles)

canons = [
    'timeline',
    'characters',
    'events',
    'myths'
]

@app.route('/canon')
def canon():
    return render_template('canon.html', canons=canons, selected_canon=None)

@app.route('/canon/<canon_name>')
def canon_type(canon_name):
    if canon_name not in canons:
        canon_name=None
    return render_template('canon.html', canons=canons, selected_canon=canon_name)

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
       articletype = request.form.get("articletype")
       articleinfo = request.form.get("info")
       guidetype = request.form.get("guidetype")
       cursor.execute(''' INSERT INTO articles VALUES(%s,%s, %s, 1, %s, %s, %s)''',(article_subject, imageurl, content, articletype, articleinfo, guidetype))
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

if __name__ == "__main__":
    app.run(port=8080, debug=True)
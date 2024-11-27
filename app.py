from flask import Flask, request, render_template, session, redirect, url_for, flash
import random
import string
import secrets
from flask import Flask, jsonify
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, UserMixin, logout_user, user_logged_out, user_unauthorized, login_required, current_user
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError

app = Flask(__name__, template_folder='templates')
app.secret_key = secrets.token_hex(32)

login_manager = LoginManager(app)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'zelda_wiki'

mysql = MySQL()
mysql.init_app(app)

@login_manager.unauthorized_handler
def unauthorized():
    flash("Please login to create an article")
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM USERS WHERE id = %s''', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(id=user[0], username=user[1], email=user[2])
    return None

@app.route('/')
def index():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT articlesubject FROM articles")
    list1 = cursor.fetchall()
    all_articles = [{'articlesubject': row[0]} for row in list1]
    latest_articles = random.sample(all_articles, 2)
    return render_template('index.html', latest_articles=latest_articles)

@app.route('/maps')
def maps():
    return render_template('maps.html')

#Guide
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

    formatted_name = name.replace("_", " ").title()
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM articles WHERE articleinfo = %s AND articletype = %s''', (formatted_name, "guide"))
    articles = cursor.fetchall()
    cursor.close()

    articles = [
        {
            'articlesubject': row[0],
            'imageURL': row[1],
            'articleText': row[2],
            'authorID': row[3],
            'articletype': row[4],
            'articleinfo': row[5],
            'guidetype': row[6]
        }
        for row in articles
    ]


    return render_template('guides.html', games=games, selected_game=name, articles=articles)

#Canon
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

    formatted_name = canon_name.replace("_", " ").title()
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM articles WHERE articleinfo = %s AND articletype = %s''', (formatted_name, "canon"))
    articles = cursor.fetchall()
    cursor.close()

    articles = [
        {
            'articlesubject': row[0],
            'imageURL': row[1],
            'articleText': row[2],
            'authorID': row[3],
            'articletype': row[4],
            'articleinfo': row[5],
            'guidetype': row[6]
        }
        for row in articles
    ]
    
    return render_template('canon.html', canons=canons, selected_canon=canon_name, articles=articles)

@app.route('/community')
def community():
    return render_template('community.html')

@app.route('/newarticle', methods=["GET", "POST"])
@login_required
def newarticle():

    if request.method == "POST":
       cursor = mysql.connection.cursor()
       article_subject = request.form.get("asubject")
       imageurl = request.form.get("iurl") 
       content = request.form.get("acontent")
       articletype = request.form.get("articletype")
       articleinfo = request.form.get("info")
       guidetype = request.form.get("guidetype")
       cursor.execute(''' INSERT INTO articles VALUES(%s,%s, %s, %s, %s, %s, %s)''',(article_subject, imageurl, content, current_user.get_id(), articletype, articleinfo, guidetype))
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

@app.route('/login', methods=["GET", "POST"])
def login():
    if(request.method == "POST"):
        cursor = mysql.connection.cursor()
        ph = PasswordHasher(hash_len = 64)
        username = request.form.get("username")
        password = request.form.get("password")

        cursor.execute('''SELECT * FROM USERS WHERE USERNAME = %s''',(username,))
        user = cursor.fetchone()
        if not user:
            flash("Username doesn't exist")
            return redirect(url_for('login'))
        
        try:
            # Verify the password using argon2
            if ph.verify(user[3], password):
                flash("Login Successful")
                userObj = User(id = user[0], email=user[2], username=user[1])
                login_user(userObj)
                return redirect(url_for('login'))
        except VerificationError:
            flash("Login Failed: Incorrect password")
            return redirect(url_for('login'))


    return render_template('login.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if(request.method == "POST"):
        cursor = mysql.connection.cursor()
        ph = PasswordHasher(hash_len=64)
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        cursor.execute(''' SELECT * FROM USERS WHERE EMAIL = %s''',(email,))
        user = cursor.fetchone()
        if user:
            flash('Email is already in use', 'danger')
            return redirect(url_for('register'))
        cursor.execute('''SELECT * FROM USERS WHERE USERNAME = %s''',(username,))
        user = cursor.fetchone()
        if user:
            flash('Username is already in use', 'danger')
            return render_template('register.html')
        cursor.execute('''INSERT INTO USERS (USERNAME, EMAIL, PASS_HASH) VALUES(%s, %s, %s)''',(username, email, ph.hash(password),))
        mysql.connection.commit()
        cursor.close()
        flash('Registration successful!\nPlease log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('You have successfully been logged out')
    return redirect(url_for('index'))

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

    def get_id(self):
        return str(self.id)



if __name__ == "__main__":
    app.run(port=8080, debug=True)
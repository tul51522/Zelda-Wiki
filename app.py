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
    next_page = request.url
    print(f'Login Managers Next Page is: {next_page}')
    flash("Please login to access this page", 'fail')
    login_url = url_for('login', next=next_page)
    return redirect(login_url)
                    
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
    cursor.execute("SELECT * FROM USERS WHERE ID = %s",(articleinfo[3],))
    username = cursor.fetchone()[1]
    return render_template('displayarticle.html', info=articleinfo, username=username)

@app.route('/login', methods=["GET", "POST"])
def login():
    print(f'Request args: {request.args}')
    if(request.method == "POST"):
        print(f'Request args: {request.args}')

        cursor = mysql.connection.cursor()
        ph = PasswordHasher(hash_len = 64)
        username = request.form.get("username")
        password = request.form.get("password")
        checkbox = request.form.get('rememberme')

        if checkbox:
            print("checkbox true")
            checked = True
        else:
            print("checkbox false")
            checked = False

        cursor.execute('''SELECT * FROM USERS WHERE USERNAME = %s''',(username,))
        user = cursor.fetchone()
        if not user:
            flash("Username doesn't exist", 'fail')
            return redirect(url_for('login'))
        
        try:
            # Verify the password using argon2
            if ph.verify(user[3], password):
                flash("Login Successful", 'success')
                userObj = User(id = user[0], email=user[2], username=user[1])
                login_user(userObj, remember = checked)

                next_page = request.args.get("next")
                print(f'Next Page is {next_page}')
                if next_page:
                    return redirect(next_page)

                return redirect(url_for('index'))
        except VerificationError:
            flash("Login Failed: Incorrect password", 'fail')
            return redirect(url_for('login'))


    return render_template('login.html', next=request.args.get("next"))

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
            flash('Email is already in use', 'fail')
            return redirect(url_for('register'))
        cursor.execute('''SELECT * FROM USERS WHERE USERNAME = %s''',(username,))
        user = cursor.fetchone()
        if user:
            flash('Username is already in use', 'fail')
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
    flash('You have successfully been logged out', 'fail')
    return redirect(url_for('index'))

@app.route('/editarticle/<name>', methods=["GET", "POST"])
@login_required
def editarticle(name):
    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT * FROM ARTICLES WHERE articlesubject = %s''',(name,))
    article = cursor.fetchone()

    if article is None:
        flash("Article not found", 'fail')
        return redirect(url_for('index'))

    articleAuthor = int(article[3])
    print("article author: ", articleAuthor)
    print("Current User ID: ", current_user.get_id())

    if (articleAuthor != int(current_user.get_id())):
        return_to = request.referrer or '/'
        flash('Only the article author can edit the article', 'fail')
        return redirect(return_to)


    if(request.method == "POST"):
        imageurl = request.form.get("iurl") 
        content = request.form.get("acontent")
        cursor.execute(''' UPDATE articles SET imageURL = %s, articleText = %s WHERE articlesubject = %s''',(imageurl,content,name,))
        mysql.connection.commit()
        

    cursor.execute(''' SELECT * FROM ARTICLES WHERE articlesubject = %s''',(name,))
    article= cursor.fetchone()

    return render_template('editarticle.html', article=article)


@app.route('/profile')
@login_required
def profile():
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM ARTICLES WHERE authorID = %s''',(current_user.get_id(),))
    articles = cursor.fetchall()
    cursor.execute('''SELECT * FROM USERS WHERE ID = %s''',(current_user.get_id(),))
    user = cursor.fetchone()
    cursor.close()
    
    return render_template('profile.html', articles=articles, user=user)

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

    def get_id(self):
        return str(self.id)



if __name__ == "__main__":
    app.run(port=8080, debug=True)
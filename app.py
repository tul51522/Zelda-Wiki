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
    return render_template('guides.html', games=games, selected_game=name)

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


if __name__ == "__main__":
    app.run(port=8080, debug=True)
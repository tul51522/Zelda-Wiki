from flask import Flask, request, render_template, session
import random
import string

app = Flask(__name__, template_folder='templates')
app.secret_key = "SOME_KEY"

@app.route('/')
def index():
    return render_template('index.html', message="index")


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
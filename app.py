from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    url_for,
)
import hashlib
from datetime import datetime, timedelta
import jwt
import os
from os.path import join, dirname
from dotenv import load_dotenv

from pymongo import MongoClient

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True


# Dummy database for demonstration purposes
# users = {'admin': 'admin_password', 'visitor': 'visitor_password'}

SECRET_KEY = 'IKMIyusuf41215753'
TOKEN_KEY = 'mytoken'


@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/logup')
def logup():
    msg = request.args.get("msg")
    return render_template("login.html", msg=msg)    
    # if request.method == 'POST':
    #     username = request.form['username']
    #     password = request.form['password']

    #     # Check if the username contains only letters
    #     if username.isalpha():
    #         if username in users and users[username] == password:
    #             return redirect(url_for('visitor_home'))
    #         else:
    #             return render_template('login.html', error='Invalid credentials for visitor.')
    #     # Check if the username contains both letters and numbers
    #     elif username.isalnum():
    #         if username in users and users[username] == password:
    #             return redirect(url_for('admin_home'))
    #         else:
    #             return render_template('logup.html', error='Invalid credentials for admin.')
    #     else:
    #         return render_template('logup.html', error='Invalid username format.')

    # return render_template('logup.html', error=None)

@app.route("/sign_in", methods=["POST"])
def sign_in():
    # Sign in
    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.users.find_one(
        {
            "username": username_receive,
            "password": pw_hash,
        }
    )
    if result:
        payload = {
            "id": username_receive,
            # the token will be valid for 24 hours
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    # Let's also handle the case where the id and
    # password combination cannot be found
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "We could not find a user with that id/password combination",
            }
        )

@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    # an api endpoint for signing up
    username_receive = request.form.get("username_give")
    fullname_receive = request.form.get("fullname_give")
    email_receive = request.form.get("email_give")
    password_receive = request.form.get("password_give")
    password_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()

    # we should save the user to the database
    doc = {
        "username": username_receive,                               # username
        "fullname": fullname_receive,                               # fullname
        "email": email_receive,                                     # email
        "password": password_hash,                                  # password
    }
    db.users.insert_one(doc)
    return jsonify({"result": "success"})

@app.route('/visitor_home')
def visitor_home():
    return jsonify({'msg': 'Welcome, Visitor!'}) 

@app.route('/admin_home')
def admin_home():
    return jsonify({'msg': 'Welcome, Admin!'}) 

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
import os
from pymongo import MongoClient
from os.path import join, dirname
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta
import hashlib
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    url_for,
)
from werkzeug.utils import secure_filename

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = '/static/profile_pics'



SECRET_KEY = os.environ.get("SECRET_KEY")
ADMIN_KEY = os.environ.get("ADMIN_KEY")
MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")
Client = MongoClient(MONGODB_URI)
db = Client.dbsparta_TGA

TOKEN_KEY = 'MYLAST'

@app.route('/')
def root():
         render_template('index1.html')
         return redirect(url_for("home"))    

@app.route('/login_user', methods=['GET'])
def login_user():
    msg = request.args.get('msg')
    return render_template('login.html', msg=msg)

@app.route('/login_admin')
def login_admin():
    msg = request.args.get('msg')
    return render_template('admin_log.html', msg=msg)

@app.route('/Gallery_nus')
def Gallery_nus():
    return render_template('Gallery.html')

# @app.route("/admin_reg")
# def admin_register():
#     token_receive = request.cookies.get("MYLAST")
#     try:
#         if token_receive:
#             payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#             user_info = db.users.find_one({'username': payload['id']})
#             if user_info:
#                 # Jika pengguna sudah login, arahkan ke halaman lain
#                 return redirect(url_for('home'))
        
#         # Jika pengguna belum login, tampilkan halaman registrasi admin
#         return render_template("admin_log.html")
    
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return render_template("admin_log.html")
        
#admin reg
@app.route("/admin_signup", methods=["POST"])
def admin_signup():
    data = request.get_json()
    username_receive = data["username_give"]    
    email_receive = data.get('email_give')
    pw_receive = data["password_give"]
    pw_hash = hashlib.sha256(pw_receive.encode("utf-8")).hexdigest()
    adminkey_receive = data.get('admin_key')

    user_exists = bool(db.users.find_one({"username": username_receive}))
    if user_exists:
        return jsonify({"result": "error_uname", "msg": f"An account with username {username_receive} is already exists. Please Login!"})
    elif adminkey_receive != ADMIN_KEY:
        return jsonify({"result": "error_akey", "msg": f"Admin key yang anda masukkan salah!"})
    else:
        doc = {
        "username": username_receive,                           
        "password": pw_hash,         
        "email": email_receive,
        "role": "admin"                                          
        }
        db.users.insert_one(doc)
        return jsonify({"result": "success"})

#user regis
@app.route("/user_signup", methods=["POST"])
def user_signup():
    data = request.get_json()
    username_receive = data["username_give"]
    fullname_receive = data.get('fullname_give')
    email_receive = data.get('email_give')
    pw_receive = data["password_give"]
    pw_hash = hashlib.sha256(pw_receive.encode("utf-8")).hexdigest()

    user_exists = bool(db.users.find_one({"username": username_receive}))
    if user_exists:
        return jsonify({"result": "error_uname", "msg": f"An account with username {username_receive} is already exists. Please Login!"})
    else:
        print(request.form)
        doc = {
        "username": username_receive,                              
        "fullname": fullname_receive,
        "email": email_receive,
        "password": pw_hash,                             
        "role": "member"                                          
        }
        db.users.insert_one(doc)
        return jsonify({"result": "success"})
    
#user login
@app.route("/sign_in", methods=["POST"])
def sign_in():
    data = request.get_json()
    username_receive = data["username_give"]
    password_receive = data["password_give"]
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.users.find_one(
        {
            "username": username_receive,
            "password": pw_hash,
        }
    )
    print(result)
    if result:
        payload = {
            "id": username_receive,
            # the token will be valid for 24 hours
            "exp": datetime.utcnow() + timedelta(seconds=60 * 15),
            "role": result["role"],
        }
        print(payload)
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
                "msg": "Kami tidak dapat menemukan pengguna dengan kombinasi username/password tersebut.",
            }
        )
    
#admin login
@app.route("/sign_in_admin", methods=["POST"])
def sign_in_admin():
    # Sign in
    data = request.get_json()
    username_receive =  data["username_give"]
    password_receive =  data["password_give"]
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.users.find_one(
        {
            "username": username_receive,
            "password": pw_hash,
        }
    )
    print(result)
    if result:
        if result["role"] != "admin":
            return jsonify(
                {
                    "result": "fail",
                    "msg": "Anda bukan admin.",
                }
            )
        payload = {
            "id": username_receive,
            # the token will be valid for 24 hours
            "exp": datetime.utcnow() + timedelta(seconds=60 * 30),
            "role": result["role"],
        }
        print(payload)
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
                "msg": "Kami tidak dapat menemukan pengguna dengan kombinasi username/password tersebut.",
            }
        )

@app.route('/home', methods=['GET'])
def home():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"username": payload["id"]})
        if user_info:
            if user_info['role'] == 'admin':
                return render_template('DATA_View.html', user_info=user_info)
            elif user_info['role'] == 'member':
                return render_template('index1.html', user_info=user_info)
        # Jika role tidak ditemukan, redirect ke halaman yang sesuai atau berikan pesan kesalahan
        return render_template('index1.html', msg="Role not found.")
    except jwt.ExpiredSignatureError:
        return render_template('index1.html', msg="Token expired. Please log in again.")
    except jwt.exceptions.DecodeError:
        return render_template('index1.html', msg="Failed to decode token. Please log in again.")

#server side for user 
@app.route('/gallery')
def gallery():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
                token_receive,
                SECRET_KEY,
                algorithms=['HS256']
            )
        user_info = db.users.find_one({'username': payload.get('id')})
        return render_template('Gallery.html', user_info=user_info)        
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):        
        return redirect(url_for('home'))


@app.route('/booking')
def booking():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
                token_receive,
                SECRET_KEY,
                algorithms=['HS256']
            )
        user_info = db.users.find_one({'username': payload.get('id')})
        return render_template('booking.html', user_info=user_info)        
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):        
        return redirect(url_for('home'))
     

@app.route('/rincian')
def rincian():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
                token_receive,
                SECRET_KEY,
                algorithms=['HS256']
            )
        user_info = db.users.find_one({'username': payload.get('id')})
        return render_template('Rincian.html', user_info=user_info)        
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):        
        return redirect(url_for('home'))
   

#server side for admin
@app.route('/data_view')
def data_view():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
                token_receive,
                SECRET_KEY,
                algorithms=['HS256']
            )
        user_info = db.users.find_one({'username': payload.get('id')})
        return render_template('Data_View.html', user_info=user_info)        
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):        
        return redirect(url_for('home'))
  

@app.route('/data_wisata')
def data_wisata():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
                token_receive,
                SECRET_KEY,
                algorithms=['HS256']
            )
        user_info = db.users.find_one({'username': payload.get('id')})
        return render_template('wisata_list.html', user_info=user_info)        
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):        
        return redirect(url_for('data_view'))
    

@app.route('/wisata_add')
def wisata_add():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
                token_receive,
                SECRET_KEY,
                algorithms=['HS256']
            )
        user_info = db.users.find_one({'username': payload.get('id')})
        return render_template('Data_add.html', user_info=user_info)        
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):        
        return redirect(url_for('data_view'))
 

@app.route('/wisata_edit')
def wisata_edit():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
                token_receive,
                SECRET_KEY,
                algorithms=['HS256']
            )
        user_info = db.users.find_one({'username': payload.get('id')})
        return render_template('Data_edit.html', user_info=user_info)        
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):        
        return redirect(url_for('data_view'))
 
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
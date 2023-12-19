import os
from pymongo import MongoClient
from flask import request
from os.path import join, dirname
from dotenv import load_dotenv
import time
from bson import ObjectId
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
    msg = request.args.get('msg')
    return render_template('Gallery.html',  msg=msg)

@app.route('/booking_nus')
def func():
    return render_template('booking.html')

# @app.route('/booking/<title>', methods=['GET'])
# def booking_title(title):
#     title_info = db.data_wisata.find_one({'title': title})    
#     return render_template('booking.html', title_info=title_info)

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
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60),
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
    
@app.route('/gallery_list', methods=['GET'])
def gallery_list():
    try:
        # Fetch data from the 'data_wisata' collection
        articles = list(db.data_wisata.find({}, {'_id': False}))

        # Return the data as JSON        
        return jsonify({'articles': articles }), 200
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({'error': 'Failed to fetch data'}), 500



# @app.route('/booking')
# def booking():
#     token_receive = request.cookies.get(TOKEN_KEY)
#     try:
#         payload = jwt.decode(
#                 token_receive,
#                 SECRET_KEY,
#                 algorithms=['HS256']
#             )
#         user_info = db.users.find_one({'username': payload.get('id')})
#         return render_template('booking.html', user_info=user_info)        
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):        
#         return redirect(url_for('home'))

# @app.route('/booking', methods=['GET'])
# def booking():
#     title = request.args.get('title')
#     token_receive = request.cookies.get(TOKEN_KEY)
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         user_info = db.users.find_one({'username': payload.get('id')})
#         title_info = db.data_wisata.find_one({'title': title})
#         if title_info is None:
#             return "Title not found", 404
#         return render_template('booking.html', user_info=user_info, title_info=title_info)
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for('home'))

@app.route('/booking/<title>', methods=['GET'])
def booking_title(title):
    title_info = db.data_wisata.find_one({'title': title})
    if title_info is None:
        return "Title not found", 404
    return render_template('booking.html',  title_info=title_info)
    # articles = db.data_wisata.find({'title': title})  # Fetch all bookings with the same title

@app.route('/booking', methods=['GET'])
def booking():
    title = request.args.get('title')
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({'username': payload.get('id')})
        title_info = db.data_wisata.find_one({'title': title})
        if title_info is None:
            return "Title not found", 404
        paket1 = title_info.get('paket1', {})
        paket2 = title_info.get('paket2', {})
        return render_template('booking.html', user_info=user_info, title_info=title_info, paket1=paket1, paket2=paket2)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))

@app.route('/request_user', methods=['POST'])
def handle_request():    
    try:
        # Retrieve form data
        file = request.form['file']
        title = request.form['title']
        description = request.form['description']
        paket = request.form['paket']
        konten = request.form['konten']
        tiket = request.form['tiket']
        harga = request.form['harga']
        status = request.form['status']
        bukti = request.form['bukti']
        # Process the form data
        doc = {
            'file': file,
            'title': title,
            'description': description,
            'paket': paket,
            'konten': konten,
            'tiket': tiket,
            'harga': harga,
            'status': status,
            'bukti' : bukti,
        }

        db.data_request.insert_one(doc) 
        return jsonify({'msg': 'sukses'}), 200
    except Exception as e:
        print(f"Terjadi kesalahan: {str(e)}")
        return jsonify({'msg': 'Failed'}), 500

# @app.route('/request_user', methods=['POST'])
# def handle_request():
#     try:
#         # Retrieve form data
#         user = request.form['user']
#         file = request.form['file']
#         title = request.form['title']
#         description = request.form['description']
#         paket = request.form['paket']
#         konten = request.form['konten']
#         tiket = request.form['tiket']
#         harga = request.form['harga']

#         # Process the form data
#         doc = {
#             'user': user,
#             'file': file,
#             'title': title,
#             'description': description,
#             'paket': paket,
#             'konten': konten,
#             'tiket': tiket,
#             'harga': harga,
#         }

#         db.data_request.insert_one(doc) 
#         return jsonify({'msg': 'sukses'}), 200
#     except Exception as e:
#         print(f"Terjadi kesalahan: {str(e)}")
#         return jsonify({'msg': 'Failed'}), 500

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


@app.route('/rincian/<title>/<paket>/<status>', methods=['GET'])
def rincian_title(title, paket, status):
    print('Paket value in rincian_title: ', paket)
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({'username': payload.get('id')})
        title_info = db.data_request.find_one({'title': title})
        if title_info is None:
            return "Title not found", 404
        # paket = title_info.het('paket', paket1)
        bukti = title_info.get('bukti', None)
        return render_template('rincian.html',  title_info=title_info, user_info=user_info, paket=paket, status=status, bukti=bukti)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):        
        return redirect(url_for('home'))


# @app.route('/rincian/<title>/<paket>/<status>', methods=['GET'])
# def rincian_title(title, paket, status):
#     token_receive = request.cookies.get(TOKEN_KEY)
#     try:
#         payload = jwt.decode(
#             token_receive,
#             SECRET_KEY,
#             algorithms=['HS256']
#         )
#         user_info = db.users.find_one({'username': payload.get('id')})
#         title_info = db.data_request.find_one({'title': title})
#         bukti = db.data_request.find_one({'bukti': bukti})
#         if title_info is None:
#             return "Title not found", 404
#         return render_template('rincian.html',  title_info=title_info, user_info=user_info, paket=paket, status=status, bukti=bukti)
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):        
#         return redirect(url_for('home'))


# @app.route('/rincian/<title>/<paket>/<status>', methods=['GET'])
# def rincian_title(title, paket, status):
#     token_receive = request.cookies.get(TOKEN_KEY)
#     try:
#         payload = jwt.decode(
#             token_receive,
#             SECRET_KEY,
#             algorithms=['HS256']
#         )
#         user_info = db.users.find_one({'username': payload.get('id')})
#         title_info = db.data_request.find_one({'title': title})
#         if title_info is None:
#             return "Title not found", 404
#         return render_template('rincian.html',  title_info=title_info, user_info=user_info, paket=paket, status=status)
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):        
#         return redirect(url_for('home'))

# @app.route('/rincian/<title>', methods=['GET'])
# def rincian_title(title):
#     token_receive = request.cookies.get(TOKEN_KEY)
#     try:
#         payload = jwt.decode(
#             token_receive,
#             SECRET_KEY,
#             algorithms=['HS256']
#         )
#         user_info = db.users.find_one({'username': payload.get('id')})
#         title_info = db.data_request.find_one({'title': title})
#         if title_info is None:
#             return "Title not found", 404
#         return render_template('rincian.html',  title_info=title_info, user_info=user_info)
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):        
#         return redirect(url_for('home'))

# @app.route('/rincian/<title>', methods=['GET'])
# def rincian_title(title):
#     title_info = db.data_request.find_one({'title': title})
#     if title_info is None:
#         return "Title not found", 404
#     return render_template('rincian.html',  title_info=title_info)
 
# @app.route('/data_request_list', methods=['GET'])
# def data_request_list():
#     try:
#         # Fetch data from the 'data_request' collection
#         requests = list(db.data_request.find({}, {'_id': False}))

#         # Return the data as JSON
#         return jsonify({'requests': requests }), 200
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
#         return jsonify({'error': 'Failed to fetch data'}), 500
   
# @app.route('/request_rincian', methods=['POST'])
# def handle_request():
#     try:
#         # Retrieve form data
#         user = request.form['user']
#         file = request.form['file']
#         title = request.form['title']
#         description = request.form['description']
#         paket = request.form['paket']
#         konten = request.form['konten']
#         tiket = request.form['tiket']
#         harga = request.form['harga']

#         # Process the form data
#         doc = {
#             'user': user,
#             'file': file,
#             'title': title,
#             'description': description,
#             'paket': paket,
#             'konten': konten,
#             'tiket': tiket,
#             'harga': harga,
#         }

#         db.data_request.insert_one(doc) 
#         return jsonify({'msg': 'sukses'}), 200
#     except Exception as e:
#         print(f"Terjadi kesalahan: {str(e)}")
#         return jsonify({'msg': 'Failed'}), 500

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


# @app.route('/find_wisata/<title>', methods=['GET'])
# def find_wisata(title):
#     try:
#         # Query the database for a document with the given title
#         wisata = db.data_wisata.find_one({'title': title})

#         # If a document with the given title was found, return it
#         if wisata is not None:
#             return jsonify(wisata), 200

#         # If no document was found, return an error message
#         return jsonify({'error': 'Wisata not found'}), 404

#     except Exception as e:
#         # If an error occurred, return an error message
#         return jsonify({'error': 'An error occurred: ' + str(e)}), 500

@app.route('/data_wisata_list', methods=['GET'])
def data_wisata_list():
    try:
        # Fetch data from the 'data_wisata' collection
        articles = list(db.data_wisata.find({}, {'_id': False}))

        # Return the data as JSON
        return jsonify({'articles': articles }), 200
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({'error': 'Failed to fetch data'}), 500

# @app.route('/data_wisata_list', methods=['GET'])
# def data_wisata_list():
#     try:
#         # Fetch data from the 'data_wisata' collection
#         articles = list(db.data_wisata.find({}, {'_id': True}))

#         # Return the data as JSON
#         return jsonify({'articles': articles }), 200
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
#         return jsonify({'error': 'Failed to fetch data'}), 500


#delete card
# @app.route('/delete_article', methods=['POST'])
# def delete_article():
#     try:
#         id = request.form['id']
#         db.data_wisata.delete_one({'_id': ObjectId(id)})
#         return jsonify({'msg': 'Deleted successfully'}), 200
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
#         return jsonify({'error': 'Failed to delete article'}), 500

# @app.route('/delete_article', methods=['POST'])
# def delete_article():
#     try:
#         id = request.form['id']
#         # Bagian kode lainnya
#         return jsonify({'msg': 'Berhasil dihapus'}), 200
#     except Exception as e:
#         print(f"Terjadi kesalahan: {str(e)}")
#         return jsonify({'error': 'Gagal menghapus artikel'}), 500

# delete card
# @app.route('/delete_article', methods=['POST'])
# def delete_article():
#     try:
#         id = request.form['id']
#         db.data_wisata.delete_one({'_id': ObjectId(id)})
#         return jsonify({'msg': 'Berhasil dihapus'}), 200
#     except Exception as e:
#         print(f"Terjadi kesalahan: {str(e)}")
#         return jsonify({'error': 'Gagal menghapus artikel', 'detail': str(e)}), 500

@app.route('/delete_card', methods=['POST'])
def delete_card():
    try:
        title_receive = request.form['title_give']
        db.data_wisata.delete_one({'title': title_receive})
        return jsonify({'msg': f'Data dengan judul {title_receive} berhasil dihapus'}), 200
    except Exception as e:
        print(f"Terjadi kesalahan: {str(e)}")
        return jsonify({'error': 'Gagal menghapus data', 'detail': str(e)}), 500

# @app.route('/update_card', methods=['POST'])
# def update_card():
#     try:
#         title_receive = request.form['title_give']
#         new_title_receive = request.form['new_title_give']
#         db.data_wisata.update_one({'title': title_receive}, {'$set': {'title': new_title_receive}})
#         return jsonify({'msg': f'Data dengan judul {title_receive} berhasil diupdate menjadi {new_title_receive}'}), 200
#     except Exception as e:
#         print(f"Terjadi kesalahan: {str(e)}")
#         return jsonify({'error': 'Gagal mengupdate data', 'detail': str(e)}), 500

# @app.route('/wisata_add')
# def wisata_add():
#     token_receive = request.cookies.get(TOKEN_KEY)
#     try:
#         payload = jwt.decode(
#                 token_receive,
#                 SECRET_KEY,
#                 algorithms=['HS256']
#             )
#         user_info = db.users.find_one({'username': payload.get('id')})
#         return render_template('Data_add.html', user_info=user_info)        
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):        
#         return redirect(url_for('data_view'))
    
@app.route('/wisata_add', methods=['GET'])
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

@app.route('/wisata_add_form', methods=['POST'])
def wisata_add_form():
    try:
        # Retrieve form data
        file = request.files["file_give"]
        extension = file.filename.split('.')[-1]
        timestamp = int(time.time())  # Get current time in seconds since the Epoch
        filename = f'static/post_{timestamp}.{extension}'  # Append the timestamp to the filename
        file.save(filename)
        title_receive = request.form['title_give']
        description_receive = request.form['description_give']

        paket1_receive = request.form['paket1_give']
        konten1_receive = request.form['description1_give']
        tiket1_receive = request.form['tiket1_give']
        harga1_receive = request.form['harga1_give']

        paket2_receive = request.form['paket2_give']
        konten2_receive = request.form['description2_give']
        tiket2_receive = request.form['tiket2_give']
        harga2_receive = request.form['harga2_give']

        # Process the form data
        doc = {
            'file': filename,
            'title': title_receive,
            'description': description_receive,
            'paket1': {
                'paket': paket1_receive,
                'konten': konten1_receive,
                'tiket': tiket1_receive,
                'harga': harga1_receive,
            },
            'paket2': {
                'paket': paket2_receive,
                'konten': konten2_receive,
                'tiket': tiket2_receive,
                'harga': harga2_receive,
            }
        }

        db.data_wisata.insert_one(doc) 
        return jsonify({'msg': 'sukses'}), 200
    except Exception as e:
        print(f"Terjadi kesalahan: {str(e)}")
        return jsonify({'msg': 'Failed'}), 500


# @app.route('/wisata_edit/<title>', methods=['GET'])
# def wisata_edit(title):
#     token_receive = request.cookies.get(TOKEN_KEY)
#     try:
#         payload = jwt.decode(
#                 token_receive,
#                 SECRET_KEY,
#                 algorithms=['HS256']
#             )
#         user_info = db.users.find_one({'username': payload.get('id')})
#         wisata_info = db.wisata.find_one({'title': title})  # Sesuaikan dengan parameter title
#         return render_template('Data_edit.html', user_info=user_info, wisata_info=wisata_info)
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):        
#         return redirect(url_for('data_view'))

# def is_valid_title(title):
#     MAX_TITLE_LENGTH = 100  # Define your own limit
#     if title and len(title) <= MAX_TITLE_LENGTH:
#         return True
#     return False

# @app.route('/wisata_update/<title>', methods=['POST'])
# def wisata_(title):
#     try:
#         # Retrieve form data
#         # Jika Anda mengganti id_receive menjadi title_receive atau sesuai dengan perubahan nama
#         title_receive = request.form['title_give'] 
#         if not is_valid_title(title_receive):
#             return jsonify({'msg': 'Invalid title'}), 400

#         # ... (lanjutkan dengan proses lainnya)
#         file = request.files["file_give"]
#         extension = file.filename.split('.')[-1]
#         timestamp = int(time.time())  # Get current time in seconds since the Epoch
#         filename = f'static/post_{timestamp}.{extension}'  # Append the timestamp to the filename
#         file.save(filename)

#         description_receive = request.form['description_give']

#         paket1_receive = request.form['paket1_give']
#         konten1_receive = request.form['description1_give']
#         tiket1_receive = request.form['tiket1_give']
#         harga1_receive = request.form['harga1_give']

#         paket2_receive = request.form['paket2_give']
#         konten2_receive = request.form['description2_give']
#         tiket2_receive = request.form['tiket2_give']
#         harga2_receive = request.form['harga2_give']
        
#         new_values = {
#             "$set": {
#                 'file': filename,
#                 'description': description_receive,
#                 'paket1': {
#                     'paket': paket1_receive,
#                     'konten': konten1_receive,
#                     'tiket': tiket1_receive,
#                     'harga': harga1_receive,
#                 },
#                 'paket2': {
#                     'paket': paket2_receive,
#                     'konten': konten2_receive,
#                     'tiket': tiket2_receive,
#                     'harga': harga2_receive,
#                 }
#             }
#         } 
#         db.data_wisata.update_one({'title': title}, new_values)  # Sesuaikan dengan perubahan nama
#         return jsonify({'msg': 'sukses'}), 200
#     except Exception as e:
#         print(f"Terjadi kesalahan: {str(e)}")
#         return jsonify({'msg': 'Failed'}), 500


# @app.route('/wisata_edit_form', methods=['POST'])
# def wisata_edit_form():
#     try:
#         # Retrieve form data
#         file = request.files["file_give"]
#         extension = file.filename.split('.')[-1]
#         timestamp = int(time.time())  # Get current time in seconds since the Epoch
#         filename = f'static/post_{timestamp}.{extension}'  # Append the timestamp to the filename
#         file.save(filename)

#         title_receive = request.form['title_give']
#         description_receive = request.form['description_give']

#         paket1_receive = request.form['paket1_give']
#         konten1_receive = request.form['description1_give']
#         tiket1_receive = request.form['tiket1_give']
#         harga1_receive = request.form['harga1_give']

#         paket2_receive = request.form['paket2_give']
#         konten2_receive = request.form['description2_give']
#         tiket2_receive = request.form['tiket2_give']
#         harga2_receive = request.form['harga2_give']

#         # Process the form data
#         new_values = {
#             "$set": {
#                 'file': filename,
#                 'description': description_receive,
#                 'paket1': {
#                     'paket': paket1_receive,
#                     'konten': konten1_receive,
#                     'tiket': tiket1_receive,
#                     'harga': harga1_receive,
#                 },
#                 'paket2': {
#                     'paket': paket2_receive,
#                     'konten': konten2_receive,
#                     'tiket': tiket2_receive,
#                     'harga': harga2_receive,
#                 }
#             }
#         }

#         db.data_wisata.update_one({'title': title_receive}, new_values)
#         return jsonify({'msg': 'sukses'}), 200
#     except Exception as e:
#         print(f"Terjadi kesalahan: {str(e)}")
#         return jsonify({'msg': 'Failed'}), 500

# @app.route('/wisata_edit_form', methods=['POST'])
# def wisata_edit_form():
#     try:
#         # Retrieve form data
#         id_receive = request.form['id_give'] 
#         file = request.files["file_give"]
#         extension = file.filename.split('.')[-1]
#         timestamp = int(time.time())  # Get current time in seconds since the Epoch
#         filename = f'static/post_{timestamp}.{extension}'  # Append the timestamp to the filename
#         file.save(filename)

#         id_receive = request.form['id_give']  # Changed from title to id
#         description_receive = request.form['description_give']

#         paket1_receive = request.form['paket1_give']
#         konten1_receive = request.form['description1_give']
#         tiket1_receive = request.form['tiket1_give']
#         harga1_receive = request.form['harga1_give']

#         paket2_receive = request.form['paket2_give']
#         konten2_receive = request.form['description2_give']
#         tiket2_receive = request.form['tiket2_give']
#         harga2_receive = request.form['harga2_give']

#         # Process the form data
#         new_values = {
#             "$set": {
#                 'file': filename,
#                 'description': description_receive,
#                 'paket1': {
#                     'paket': paket1_receive,
#                     'konten': konten1_receive,
#                     'tiket': tiket1_receive,
#                     'harga': harga1_receive,
#                 },
#                 'paket2': {
#                     'paket': paket2_receive,
#                     'konten': konten2_receive,
#                     'tiket': tiket2_receive,
#                     'harga': harga2_receive,
#                 }
#             }
#         } 
#         db.data_wisata.update_one({'_id': ObjectId(id_receive)}, new_values)  # Changed from title to id
#         return jsonify({'msg': 'sukses'}), 200
#     except Exception as e:
#         print(f"Terjadi kesalahan: {str(e)}")
#         return jsonify({'msg': 'Failed'}), 500
#     if not is_valid_object_id(id_receive):
#         return jsonify({'msg': 'Invalid id'}), 400
 
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
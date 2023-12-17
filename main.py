from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from pymongo import MongoClient
import jwt
from jwt.exceptions import ExpiredSignatureError
from datetime import datetime, timedelta
import hashlib
from bson import ObjectId
 


Client = MongoClient("mongodb://hider:12345@ac-cne9chv-shard-00-00.v3veas6.mongodb.net:27017,ac-cne9chv-shard-00-01.v3veas6.mongodb.net:27017,ac-cne9chv-shard-00-02.v3veas6.mongodb.net:27017/?ssl=true&replicaSet=atlas-b2pqmh-shard-0&authSource=admin&retryWrites=true&w=majority")
db = Client.dbProject_akhir

SECRET_KEY = 'MYWEB'

app = Flask(__name__)

@app.route('/')
def home():
    user = {'logged': 'username' in session}
    return render_template('Index1.html', user=user)

@app.route('/Gallery')
def gallery():
    user = {'logged': 'username' in session}
    return render_template('Gallery.html', user=user)

@app.route('/Booking')
def booking():
    user = {'logged': 'username' in session}
    return render_template('booking.html', user=user)

@app.route('/Rincian')
def Rincian():
    user = {'logged': 'username' in session}
    return render_template('Rincian.html', user=user)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_receive = request.form.get("username_give")
        password_receive = request.form.get("password_give")
        pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
        user = db.users.find_one({"username": username_receive, "password": pw_hash})
        if user:
            session['username'] = username_receive
            return redirect(url_for('home'))
        else:
            return "Login failed"
    else:
        if 'username' in session:
            return redirect(url_for('home'))
        return render_template("login.html")

@app.route("/sign_in", methods=["POST"])
def sign_in():
    username_receive = request.form.get("username_give")
    password_receive = request.form.get("password_give")
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    user = db.users.find_one({"username": username_receive, "password": pw_hash})
    
    if user:
        payload = {
            "id": username_receive,
            "exp": datetime.utcnow() + timedelta(seconds=60 * 15),  # Token berlaku selama 15 menit
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "Login failed. Invalid username or password.",
            }
        )

@app.route('/sign_up', methods=['POST'])
def sign_up():
    username_receive = request.form.get('username_give')
    password_receive = request.form.get('password_give')
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    fullname_receive = request.form.get('fullname_give')
    email_receive = request.form.get('email_give')
    role_receive = 'admin' if 'admin' in username_receive else 'user'

    if username_receive and password_receive:           
        doc = {
            "username": username_receive,                                
            "password": pw_hash,
            "fullname": fullname_receive,
            "email" : email_receive,
            "role" : role_receive                  
        }
        db.users.insert_one(doc)    
        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "fail", "msg": "Username and password are required."})

# @app.route('/gallery_list', methods=['GET'])
# def gallery_list():
#     articles = list(db.data_wisata.find({}, {'_id': False}))
#     return jsonify({'articles': articles})

@app.route('/gallery_list', methods=['GET'])
def gallery_list():
    articles = list(db.data_wisata.find({}, {'_id': True, 'title': True, 'description': True, 'file': True, 'paket1.harga': True}))
    formatted_articles = [
        {
            'id': str(article['_id']),
            'title': article['title'],
            'description': article['description'],
            'file': article['file'],
            'harga_paket1': article['paket1']['harga']
        }
        for article in articles
    ]
    return jsonify({'articles': formatted_articles})


@app.route('/get_details', methods=['GET'])
def get_details():
    card_id = request.args.get('cardId')
    article = db.data_wisata.find_one({'_id': ObjectId(card_id)}, {'_id': False})
    
    if article:
        return jsonify({'details': article})
    else:
        return jsonify({'error': 'Article not found'}), 404
    


@app.route('/wisata_add', methods=['POST'])
def data_add():
    try:
        # Retrieve form data
        file = request.files["file_give"]
        extension = file.filename.split('.')[-1]
        filename = f'static/post.{extension}'
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

 

@app.route('/wisata_Update', methods=['POST'])
def wisata_Update():
    try:
        # Retrieve form data
        file = request.files["file_give"]
        extension = file.filename.split('.')[-1]
        filename = f'static/post.{extension}'
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

        # Ambil ID dari permintaan
        data_id = request.form.get('id')

        # Lakukan pembaruan di database
        result = db.data_wisata.update_one({'_id': ObjectId(data_id)}, {'$set': doc})

        if result.modified_count > 0:
            return jsonify({'msg': 'Data berhasil diperbarui'}), 200
        else:
            return jsonify({'msg': 'Data tidak ditemukan atau tidak ada perubahan'}), 404
    except Exception as e:
        print(f"Terjadi kesalahan: {str(e)}")
        return jsonify({'msg': 'Failed'}), 500



@app.route('/delete_wisata', methods=['POST'])
def delete_wisata():
    try:
        # Ambil ID dari permintaan
        data_id = request.form.get('id')
        
        # Lakukan penghapusan di database
        result = db.data_wisata.delete_one({'_id': ObjectId(data_id)})

        if result.deleted_count > 0:
            return jsonify({'msg': 'Data berhasil dihapus'}), 200
        else:
            return jsonify({'msg': 'Data tidak ditemukan atau sudah dihapus'}), 404
    except Exception as e:
        print(f"Terjadi kesalahan: {str(e)}")
        return jsonify({'msg': 'Gagal menghapus data'}), 500



@app.route('/booking_show', methods=['GET'])
def booking_show():
    articles = list(db.data_wisata.find({}, {'_id': False}))
    return jsonify({'articles': articles})

@app.route('/wisata_show', methods=['GET'])
def show_show():
    articles = list(db.data_wisata.find({}, {'_id': False}))
    return jsonify({'articles': articles})

@app.route('/wisata_request')
def wisata_request():
    # Mengambil data wisata dari koleksi 'data_wisata'
    data_wisata = list(db.data_wisata.find({}, {'_id': False}))

    # Mengambil data pengguna berdasarkan username dari koleksi 'users'
    username = "nama_pengguna_anda"
    user_data = db.users.find_one({'username': username}, {'_id': False})

    # Menggabungkan data wisata dan data pengguna
    articles = {'data_wisata': data_wisata, 'user_data': user_data}

    return jsonify({'articles': articles})


# @app.route('/wisata_edit/<id>', methods=['POST'])
# def data_edit(id):
#     try:
#         # Retrieve form data for editing
#         file = request.files["file_give"]
#         extension = file.filename.split('.')[-1]
#         filename = f'static/post.{extension}'
#         file.save(filename)
#         title_receive = request.form['title_give']
#         description_receive = request.form['description_give']

#         paket1_receive = request.form['paket1_give']
#         description1_receive = request.form['description1_give']
#         tiket1_receive = request.form['tiket1_give']
#         harga1_receive = request.form['harga1_give']

#         paket2_receive = request.form['paket2_give']
#         description2_receive = request.form['description2_give']
#         tiket2_receive = request.form['tiket2_give']
#         harga2_receive = request.form['harga2_give']

#         # Process the form data
#         doc = {
#             'file': filename,
#             'title': title_receive,
#             'description': description_receive,
#             'paket1': {
#                 'paket': paket1_receive,
#                 'description': description1_receive,
#                 'tiket': tiket1_receive,
#                 'harga': harga1_receive,
#             },
#             'paket2': {
#                 'paket': paket2_receive,
#                 'description': description2_receive,
#                 'tiket': tiket2_receive,
#                 'harga': harga2_receive,
#             }
#         }

#         # Update the existing document in the database
#         db.data_wisata.update_one({'_id': ObjectId(id)}, {"$set": doc})

#         return jsonify({'msg': 'sukses'}), 200
#     except Exception as e:
#         print(f"Terjadi kesalahan: {str(e)}")
#         return jsonify({'msg': 'Failed'}), 500

# @app.route('/dashboard')
# def dashboard():
#     if 'username' in session:
#         return render_template('dasboard.html', isLoggedIn=True)
#     else:
#         return redirect(url_for('login'))
    
@app.route('/wisata_edit')
def data_edit():
        return render_template('Data_edit.html')
    
@app.route('/wisata_add')
def wisata_add():
        return render_template('Data_add.html')

@app.route('/wisata_list')
def wisata_list():
        return render_template('wisata_list.html')

@app.route('/wisata_view')
def wisata_view():
        return render_template('DATA_View.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

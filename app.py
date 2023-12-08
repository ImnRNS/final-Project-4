from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

client = MongoClient("mongodb://hider:12345@ac-cne9chv-shard-00-00.v3veas6.mongodb.net:27017,ac-cne9chv-shard-00-01.v3veas6.mongodb.net:27017,ac-cne9chv-shard-00-02.v3veas6.mongodb.net:27017/?ssl=true&replicaSet=atlas-b2pqmh-shard-0&authSource=admin&retryWrites=true&w=majority")
db = client['dbProject-final']

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/paket', methods=['GET'])
def show_diary():
    articles = list(db.diary.find({}, {'_id': False}))
    return jsonify({'articles': articles})

@app.route('/paket', methods=['POST'])
def save_paket():
    title_receive = request.form["title_give"]
    content_receive = request.form["content_give"]
    file = request.files["file_give"]

    paket1_receive = request.form["paket1_give"]
    harga1_receive = request.form["harga1_give"]
    deskripsi1_receive = request.form["deskripsi1_give"]
    tiket1_receive = request.form["tiket1_give"]

    paket2_receive = request.form["paket2_give"]
    harga2_receive = request.form["harga2_give"]
    deskripsi2_receive = request.form["deskripsi2_give"]
    tiket2_receive = request.form["tiket2_give"]

    paket3_receive = request.form["paket3_give"]
    harga3_receive = request.form["harga3_give"]
    deskripsi3_receive = request.form["deskripsi3_give"]
    tiket3_receive = request.form["tiket3_give"]

    doc = {
        'title': title_receive,
        'content': content_receive,
        'file': file.filename,
        'paket1': {
            'paket': paket1_receive,
            'harga': harga1_receive,
            'deskripsi': deskripsi1_receive,
            'tiket': tiket1_receive
        },
        'paket2': {
            'paket': paket2_receive,
            'harga': harga2_receive,
            'deskripsi': deskripsi2_receive,
            'tiket': tiket2_receive
        },
        'paket3': {
            'paket': paket3_receive,
            'harga': harga3_receive,
            'deskripsi': deskripsi3_receive,
            'tiket': tiket3_receive
        }
    }

    db.Booking.insert_one(doc)

    return jsonify({'msg': 'Upload complete!'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

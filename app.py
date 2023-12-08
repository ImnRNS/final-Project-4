from flask import Flask, render_template, request
from pymongo import MongoClient
from datetime import datetime, timedelta
import hashlib

import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)

@app.route('/logup')
def logup():
    return render_template('logup.html')

@app.route('/gallery_page')
def gallery_page():
    return render_template('Gallery_page.html')

@app.route('/booking')
def booking():
    return render_template('booking.html')

# admin route
@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/user_data')
def user_data():
    return render_template('user_data.html')

@app.route('/tourism_data')
def tourism_data():
    return render_template('tourism_data.html')

@app.route('/datawisata_list')
def datawisata_list():
    return render_template('datawisata_list.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
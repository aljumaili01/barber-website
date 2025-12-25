import json
import hashlib
import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

# إعداد المسارات لتقرأ من المجلد الرئيسي مباشرة
app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')
app.secret_key = 'lion_king_2025'

DATA_FILE = 'site_data.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"hero_title": "مرحبا بك", "hero_desc": "صالون الحلاقة", "barbers": [], "gallery_images": []}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/')
def index():
    # هنا Flask سيبحث عن index.html في المجلد الرئيسي
    return render_template('index.html', site_data=load_data())

@app.route('/admin_login')
def admin_login():
    return render_template('admin_login.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

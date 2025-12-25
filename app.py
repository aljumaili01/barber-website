import json
import hashlib
import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')
app.secret_key = 'lion_king_2025'

DATA_FILE = 'site_data.json'
ADMIN_DATA_FILE = 'admin_data.json'

def load_data(filename):
    if not os.path.exists(filename):
        if filename == DATA_FILE:
            return {"hero_title": "مرحبا بك", "hero_desc": "صالون الحلاقة", "barbers": [], "gallery_images": [], "extra_texts": {}}
        return {"username": "admin", "password_hash": hashlib.sha256("1234".encode()).hexdigest()}
    with open(filename, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return {}

@app.route('/')
def index():
    return render_template('index.html', site_data=load_data(DATA_FILE))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('username') == 'admin' and request.form.get('password') == '1234':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
    return render_template('admin_login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('dashboard.html', site_data=load_data(DATA_FILE))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

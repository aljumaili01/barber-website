from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import os
import hashlib

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = "aslan_barber_ultra_secure_2025"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DATA_FILE = os.path.join(BASE_DIR, 'site_data.json')
ADMIN_DATA_FILE = os.path.join(BASE_DIR, 'admin_data.json')

# دالة تحميل البيانات
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# دالة حفظ البيانات
def save_data(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    return render_template('index.html', site_data=load_data(SITE_DATA_FILE))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        user_input = request.form.get('username')
        pass_input = request.form.get('password')
        admin_data = load_data(ADMIN_DATA_FILE)
        
        # تشفير كلمة المرور للمقارنة
        input_hash = hashlib.sha256(pass_input.encode()).hexdigest()
        
        if user_input == admin_data.get('username') and input_hash == admin_data.get('password_hash'):
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        return "بيانات الدخول خاطئة!"
    return render_template('admin_login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('dashboard.html', site_data=load_data(SITE_DATA_FILE))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# --- روابط الـ API المطلوبة للـ Dashboard ---

@app.route('/api/update_texts', methods=['POST'])
def update_texts():
    data = load_data(SITE_DATA_FILE)
    req = request.json
    data['hero_title'] = req.get('hero_title')
    data['hero_desc'] = req.get('hero_desc')
    save_data(SITE_DATA_FILE, data)
    return jsonify({"success": True, "message": "تم تحديث النصوص بنجاح"})

@app.route('/api/add_barber', methods=['POST'])
def add_barber():
    data = load_data(SITE_DATA_FILE)
    data['barbers'].append(request.json)
    save_data(SITE_DATA_FILE, data)
    return jsonify({"success": True, "message": "تم إضافة الحلاق"})

@app.route('/api/delete_barber/<name>', methods=['DELETE'])
def delete_barber(name):
    data = load_data(SITE_DATA_FILE)
    data['barbers'] = [b for b in data['barbers'] if b['name'] != name]
    save_data(SITE_DATA_FILE, data)
    return jsonify({"success": True, "message": "تم حذف الحلاق"})

@app.route('/api/update_about', methods=['POST'])
def update_about():
    data = load_data(SITE_DATA_FILE)
    req = request.json
    if 'extra_texts' not in data: data['extra_texts'] = {}
    data['extra_texts'].update(req)
    save_data(SITE_DATA_FILE, data)
    return jsonify({"success": True, "message": "تم تحديث قسم معلومات عنا"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

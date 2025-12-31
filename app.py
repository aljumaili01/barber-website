from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import os
import hashlib

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = "aslan_barber_ultra_secure_2025"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DATA_FILE = os.path.join(BASE_DIR, 'site_data.json')
ADMIN_DATA_FILE = os.path.join(BASE_DIR, 'admin_data.json')

def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

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

# --- روابط الـ API التي يطلبها كود الداش بورد الخاص بك ---

@app.route('/api/update_texts', methods=['POST'])
def update_texts():
    data = load_data(SITE_DATA_FILE)
    req = request.json
    data['hero_title'] = req.get('hero_title')
    data['hero_desc'] = req.get('hero_desc')
    save_data(SITE_DATA_FILE, data)
    return jsonify({"success": True, "message": "تم تحديث النصوص بنجاح"})

@app.route('/api/update_about', methods=['POST'])
def update_about():
    data = load_data(SITE_DATA_FILE)
    if 'extra_texts' not in data: data['extra_texts'] = {}
    data['extra_texts'].update(request.json)
    save_data(SITE_DATA_FILE, data)
    return jsonify({"success": True, "message": "تم تحديث قسم معلومات عنا"})

@app.route('/api/add_barber', methods=['POST'])
def add_barber():
    data = load_data(SITE_DATA_FILE)
    data['barbers'].append(request.json)
    save_data(SITE_DATA_FILE, data)
    return jsonify({"success": True, "message": "تم إضافة الحلاق"})

@app.route('/api/update_barber', methods=['POST'])
def update_barber():
    data = load_data(SITE_DATA_FILE)
    req = request.json
    for barber in data['barbers']:
        if barber['name'] == req['old_name']:
            barber.update({k: v for k, v in req.items() if k != 'old_name'})
            break
    save_data(SITE_DATA_FILE, data)
    return jsonify({"success": True, "message": "تم تحديث بيانات الحلاق"})

@app.route('/api/delete_barber/<name>', methods=['DELETE'])
def delete_barber(name):
    data = load_data(SITE_DATA_FILE)
    data['barbers'] = [b for b in data['barbers'] if b['name'] != name]
    save_data(SITE_DATA_FILE, data)
    return jsonify({"success": True, "message": "تم حذف الحلاق"})

@app.route('/api/add_image', methods=['POST'])
def add_image():
    data = load_data(SITE_DATA_FILE)
    data['gallery_images'].append(request.json)
    save_data(SITE_DATA_FILE, data)
    return jsonify({"success": True, "message": "تم إضافة الصورة للمعرض"})

@app.route('/api/delete_image/<filename>', methods=['DELETE'])
def delete_image(filename):
    data = load_data(SITE_DATA_FILE)
    data['gallery_images'] = [img for img in data['gallery_images'] if img['filename'] != filename]
    save_data(SITE_DATA_FILE, data)
    return jsonify({"success": True, "message": "تم حذف الصورة"})

@app.route('/api/add_text', methods=['POST'])
def add_text():
    data = load_data(SITE_DATA_FILE)
    data['extra_texts'][request.json['key']] = request.json['value']
    save_data(SITE_DATA_FILE, data)
    return jsonify({"success": True, "message": "تم إضافة النص"})

@app.route('/api/delete_text/<key>', methods=['DELETE'])
def delete_text(key):
    data = load_data(SITE_DATA_FILE)
    if key in data['extra_texts']: del data['extra_texts'][key]
    save_data(SITE_DATA_FILE, data)
    return jsonify({"success": True, "message": "تم حذف النص"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

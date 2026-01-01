from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = "aslan_barber_ultra_secure_2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DATA_FILE = os.path.join(BASE_DIR, 'site_data.json')

def load_data():
    if os.path.exists(SITE_DATA_FILE):
        with open(SITE_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"hero_title": "", "hero_desc": "", "barbers": [], "gallery_images": [], "extra_texts": {}}

def save_data(data):
    with open(SITE_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    return render_template('index.html', site_data=load_data())

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('username') == 'admin' and request.form.get('password') == '123':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        return "بيانات الدخول خاطئة!"
    return render_template('admin_login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('dashboard.html', site_data=load_data())

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# --- الأكواد البرمجية (APIs) التي تطلبها لوحة التحكم الخاصة بك ---

@app.route('/api/update_texts', methods=['POST'])
def update_texts():
    data = load_data()
    data['hero_title'] = request.json.get('hero_title')
    data['hero_desc'] = request.json.get('hero_desc')
    save_data(data)
    return jsonify({"success": True, "message": "تم حفظ النصوص بنجاح"})

@app.route('/api/update_about', methods=['POST'])
def update_about():
    data = load_data()
    if 'extra_texts' not in data: data['extra_texts'] = {}
    data['extra_texts'].update(request.json)
    save_data(data)
    return jsonify({"success": True, "message": "تم تحديث معلومات عنا"})

@app.route('/api/add_barber', methods=['POST'])
def add_barber():
    data = load_data()
    data['barbers'].append(request.json)
    save_data(data)
    return jsonify({"success": True, "message": "تم إضافة الحلاق بنجاح"})

@app.route('/api/update_barber', methods=['POST'])
def update_barber():
    data = load_data()
    req = request.json
    for b in data['barbers']:
        if b['name'] == req['old_name']:
            b.update({k: v for k, v in req.items() if k != 'old_name'})
            break
    save_data(data)
    return jsonify({"success": True, "message": "تم تحديث بيانات الحلاق"})

@app.route('/api/delete_barber/<name>', methods=['DELETE'])
def delete_barber(name):
    data = load_data()
    data['barbers'] = [b for b in data['barbers'] if b['name'] != name]
    save_data(data)
    return jsonify({"success": True, "message": "تم حذف الحلاق"})

@app.route('/api/add_image', methods=['POST'])
def add_image():
    data = load_data()
    data['gallery_images'].append(request.json)
    save_data(data)
    return jsonify({"success": True, "message": "تم إضافة الصورة للمعرض"})

@app.route('/api/delete_image/<filename>', methods=['DELETE'])
def delete_image(filename):
    data = load_data()
    data['gallery_images'] = [img for img in data['gallery_images'] if img['filename'] != filename]
    save_data(data)
    return jsonify({"success": True, "message": "تم حذف الصورة"})

@app.route('/api/add_text', methods=['POST'])
def add_text():
    data = load_data()
    data['extra_texts'][request.json['key']] = request.json['value']
    save_data(data)
    return jsonify({"success": True, "message": "تم إضافة النص الجديد"})

@app.route('/api/delete_text/<key>', methods=['DELETE'])
def delete_text(key):
    data = load_data()
    if key in data['extra_texts']: del data['extra_texts'][key]
    save_data(data)
    return jsonify({"success": True, "message": "تم حذف النص"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

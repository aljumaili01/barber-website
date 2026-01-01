from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = "aslan_barber_2026_final"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DATA_FILE = os.path.join(BASE_DIR, 'site_data.json')

def load_data():
    default_data = {
        "hero_title": "صالون الأسد",
        "hero_desc": "أهلاً بكم",
        "barbers": [],
        "gallery_images": [],
        "extra_texts": {}
    }
    if os.path.exists(SITE_DATA_FILE):
        try:
            with open(SITE_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default_data
    return default_data

def save_data(data):
    with open(SITE_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    return render_template('index.html', site_data=load_data())

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')
        if user == 'admin' and pwd == '123':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        return "خطأ في البيانات! <a href='/admin_login'>حاول مجدداً</a>"
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

# --- API Routes ---
@app.route('/api/update_texts', methods=['POST'])
def update_texts():
    data = load_data()
    data.update(request.json)
    save_data(data)
    return jsonify({"success": True, "message": "تم التحديث"})

@app.route('/api/add_barber', methods=['POST'])
def add_barber():
    data = load_data()
    data['barbers'].append(request.json)
    save_data(data)
    return jsonify({"success": True, "message": "تم إضافة الحلاق"})

@app.route('/api/delete_barber/<name>', methods=['DELETE'])
def delete_barber(name):
    data = load_data()
    data['barbers'] = [b for b in data['barbers'] if b['name'] != name]
    save_data(data)
    return jsonify({"success": True, "message": "تم الحذف"})

@app.route('/api/add_image', methods=['POST'])
def add_image():
    data = load_data()
    data['gallery_images'].append(request.json)
    save_data(data)
    return jsonify({"success": True, "message": "تمت إضافة الصورة"})

@app.route('/api/delete_image/<filename>', methods=['DELETE'])
def delete_image(filename):
    data = load_data()
    data['gallery_images'] = [i for i in data['gallery_images'] if i['filename'] != filename]
    save_data(data)
    return jsonify({"success": True, "message": "تم حذف الصورة"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

import json
import hashlib
import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

# التعديل: إخبار Flask أن الملفات موجودة في المجلد الرئيسي مباشرة
app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')
app.secret_key = 'your_secret_key_2025' # يمكنك تغيير هذا لاحقاً

DATA_FILE = 'site_data.json'
ADMIN_DATA_FILE = 'admin_data.json'

# --- الدوال المساعدة لتحميل وحفظ البيانات ---

def load_data(filename):
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    if filename == DATA_FILE:
        return {
            "hero_title": "مرحبا بك في صالون أسد الحلاق",
            "hero_desc": "نقدم أفضل خدمات قص الشعر وحلاقة الذقن بأيدي أمهر الحلاقين.",
            "barbers": [
                {"name": "مصطفى", "phone": "555-1234", "image": "kuafor_mustafa.jpg.jpg", "instagram": "mustafa_barber"},
                {"name": "قاسم", "phone": "555-5678", "image": "kuafor_qasim.jpg.jpg", "instagram": "qasim_barber"},
                {"name": "رائد", "phone": "555-9012", "image": "kuafor_raed.jpg.jpg", "instagram": "raed_barber"},
            ],
            "gallery_images": [
                {"filename": "kuafor_mustafa.jpg.jpg", "barber_name": "مصطفى"},
                {"filename": "kuafor_qasim.jpg.jpg", "barber_name": "قاسم"},
                {"filename": "kuafor_raed.jpg.jpg", "barber_name": "رائد"},
            ],
            "extra_texts": {
                "about_title": "ما يميز صالوننا",
                "about_image1": "about1.jpg",
                "about_desc_card1": "خبرة تزيد عن 10 سنوات في مجال الحلاقة والتجميل، نضمن لك إطلالة عصرية ومتميزة.",
                "about_image2": "about2.jpg",
                "about_desc_card2": "نستخدم أحدث الأدوات وأجود المنتجات لضمان سلامتك وراحتك.",
                "opening_hours": "يومياً من 9:00 صباحاً حتى 10:00 مساءً",
                "address": "اسطنبول، الفاتح، شارع الاستقلال",
            }
        }
    elif filename == ADMIN_DATA_FILE:
        hashed_password = hashlib.sha256("1234".encode()).hexdigest()
        return {"username": "admin", "password_hash": hashed_password}
    return {}

def save_data(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# تحميل البيانات الأولية
site_data = load_data(DATA_FILE)
admin_data = load_data(ADMIN_DATA_FILE)

# --- دوال المصادقة ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(username, password):
    if username == admin_data.get('username'):
        return admin_data.get('password_hash') == hash_password(password)
    return False

def is_logged_in():
    return session.get('logged_in')

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return wrapper

# --- المسارات ---
@app.route('/')
def index():
    return render_template('index.html', site_data=load_data(DATA_FILE))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_password(username, password):
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        return render_template('admin_login.html', error="اسم المستخدم أو كلمة السر غير صحيح.")
    return render_template('admin_login.html', error=None)

@app.route('/dashboard')
@admin_required
def dashboard():
    return render_template('dashboard.html', site_data=load_data(DATA_FILE))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# --- API Endpoints (مختصرة للعمل) ---
@app.route('/api/update_texts', methods=['POST'])
@admin_required
def update_texts():
    data = request.json
    current_data = load_data(DATA_FILE)
    current_data['hero_title'] = data.get('hero_title', current_data['hero_title'])
    current_data['hero_desc'] = data.get('hero_desc', current_data['hero_desc'])
    save_data(current_data, DATA_FILE)
    return jsonify({"success": True})

# --- تشغيل التطبيق بما يتوافق مع Render ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

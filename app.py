from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
app.secret_key = "aslan_barber_2025"

# تحديد المسار الكامل لملف البيانات لضمان وصول السيرفر إليه
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')

def load_data():
    """تحميل البيانات مع معالجة الأخطاء لمنع تعطل السيرفر"""
    if not os.path.exists(DATA_FILE):
        # في حال عدم وجود الملف، سيقوم السيرفر بإنشاء هذه البيانات فوراً
        initial_data = {
            "admin_password": "123",
            "hero_title": "صالون الأسد للحلاقة",
            "hero_desc": "أفضل تجربة حلاقة في المنطقة.",
            "barbers": [
                {"name": "قاسم", "phone": "05354057831", "image": "kuafor_qasim.jpg", "instagram": ""},
                {"name": "رائد", "phone": "05011087030", "image": "kuafor_raed.jpg", "instagram": ""},
                {"name": "مصطفى", "phone": "05315969753", "image": "kuafor_mustafa.jpg", "instagram": ""},
                {"name": "حيدر", "phone": "05383686314", "image": "kuafor_hayder.jpeg", "instagram": ""}
            ],
            "gallery_images": [],
            "extra_texts": {"opening_hours": "9:00 AM - 10:00 PM", "address": "اسطنبول"}
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=4)
        return initial_data

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"barbers": [], "hero_title": "Error Loading Data"}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    try:
        site_data = load_data()
        return render_template('index.html', site_data=site_data)
    except Exception as e:
        return f"خطأ في تحميل الصفحة الرئيسية: {str(e)}"

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    site_data = load_data()
    if request.method == 'POST':
        password = request.form.get('password')
        if password == site_data.get('admin_password', '123'):
            return redirect(url_for('dashboard'))
        return "كلمة المرور خاطئة!"
    return render_template('admin_login.html')

@app.route('/dashboard')
def dashboard():
    site_data = load_data()
    return render_template('dashboard.html', site_data=site_data)

@app.route('/add_barber', methods=['POST'])
def add_barber():
    if request.method == 'POST':
        site_data = load_data()
        new_barber = {
            "name": request.form.get('name'),
            "phone": request.form.get('phone'),
            "instagram": request.form.get('instagram', ''),
            "image": "kuafor_mustafa.jpg"
        }
        site_data['barbers'].append(new_barber)
        save_data(site_data)
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

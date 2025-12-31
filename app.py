from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
app.secret_key = "aslan_barber_secret_key"

# اسم ملف البيانات
DATA_FILE = 'data.json'

def load_data():
    """وظيفة لقراءة البيانات من ملف data.json"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # بيانات احتياطية في حال فقدان الملف
        return {"barbers": [], "hero_title": "صالون الأسد", "admin_password": "123"}

def save_data(data):
    """وظيفة لحفظ البيانات المحدثة في ملف data.json"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    # تحميل أحدث البيانات (بما في ذلك حيدر وأي حلاق جديد)
    site_data = load_data()
    return render_template('index.html', site_data=site_data)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    site_data = load_data()
    if request.method == 'POST':
        password = request.form.get('password')
        # التحقق من كلمة المرور الموجودة داخل data.json
        if password == site_data.get('admin_password', '123'):
            return redirect(url_for('dashboard'))
        else:
            return "كلمة المرور خاطئة! <a href='/admin_login'>حاول ثانية</a>"
    return render_template('admin_login.html')

@app.route('/dashboard')
def dashboard():
    site_data = load_data()
    return render_template('dashboard.html', site_data=site_data)

@app.route('/add_barber', methods=['POST'])
def add_barber():
    if request.method == 'POST':
        site_data = load_data()
        
        # إنشاء بيانات الحلاق الجديد من النموذج
        new_barber = {
            "name": request.form.get('name'),
            "phone": request.form.get('phone'),
            "instagram": request.form.get('instagram', ''),
            "image": "kuafor_mustafa.jpg" # صورة افتراضية
        }
        
        # إضافة الحلاق للقائمة وحفظ الملف فوراً
        site_data['barbers'].append(new_barber)
        save_data(site_data)
        
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

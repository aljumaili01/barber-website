import json
import hashlib
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # يجب تغيير هذا المفتاح في الإنتاج

DATA_FILE = 'site_data.json'
ADMIN_DATA_FILE = 'admin_data.json'

# --- الدوال المساعدة لتحميل وحفظ البيانات ---

def load_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        if filename == DATA_FILE:
            # البيانات الافتراضية للموقع (تم استعادة بيانات الحلاقين مع أسماء الملفات المؤكدة)
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
            # البيانات الافتراضية للمدير
            hashed_password = hashlib.sha256("1234".encode()).hexdigest()
            return {"username": "admin", "password_hash": hashed_password}
        return {}

def save_data(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- تحميل البيانات عند بدء التشغيل ---
site_data = load_data(DATA_FILE)
admin_data = load_data(ADMIN_DATA_FILE)

# --- دوال المصادقة ---

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(username, password):
    if username == admin_data['username']:
        return admin_data['password_hash'] == hash_password(password)
    return False

def is_logged_in():
    return 'logged_in' in session and session['logged_in']

def admin_required(f):
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# --- المسارات العامة (الموقع) ---

@app.route('/')
def index():
    return render_template('index.html', site_data=site_data)

# --- مسارات الإدارة ---

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
    global site_data
    site_data = load_data(DATA_FILE) # إعادة تحميل للتأكد من أحدث نسخة
    return render_template('dashboard.html', site_data=site_data)

@app.route('/logout')
@admin_required
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# --- API Endpoints ---

@app.route('/api/change_password', methods=['POST'])
@admin_required
def change_password():
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    # 1. التحقق من كلمة السر الحالية (تم الإصلاح النهائي لخطأ global)
    if not check_password('admin', current_password):
        return jsonify({"success": False, "message": "كلمة السر الحالية غير صحيحة."}), 400

    # 2. التصريح بـ 'global' قبل التعديل
    global admin_data
    
    # 3. تعديل admin_data وحفظه
    admin_data['password_hash'] = hash_password(new_password)
    save_data(admin_data, ADMIN_DATA_FILE)
    return jsonify({"success": True, "message": "تم تغيير كلمة السر بنجاح. يرجى تسجيل الدخول مجدداً."})

@app.route('/api/update_texts', methods=['POST'])
@admin_required
def update_texts():
    data = request.json
    global site_data
    site_data['hero_title'] = data.get('hero_title', site_data['hero_title'])
    site_data['hero_desc'] = data.get('hero_desc', site_data['hero_desc'])
    save_data(site_data, DATA_FILE)
    return jsonify({"success": True, "message": "تم حفظ نصوص الصفحة الرئيسية بنجاح."})

# --- الدالة المحدثة لتحديث قسم معلومات عنا ---
@app.route('/api/update_about', methods=['POST'])
@admin_required
def update_about():
    data = request.json
    global site_data

    if 'extra_texts' not in site_data:
        site_data['extra_texts'] = {}
        
    site_data['extra_texts']['about_title'] = data.get('about_title', site_data['extra_texts'].get('about_title', ''))
    site_data['extra_texts']['about_image1'] = data.get('about_image1', site_data['extra_texts'].get('about_image1', ''))
    site_data['extra_texts']['about_desc_card1'] = data.get('about_desc_card1', site_data['extra_texts'].get('about_desc_card1', ''))
    site_data['extra_texts']['about_image2'] = data.get('about_image2', site_data['extra_texts'].get('about_image2', ''))
    site_data['extra_texts']['about_desc_card2'] = data.get('about_desc_card2', site_data['extra_texts'].get('about_desc_card2', ''))

    save_data(site_data, DATA_FILE)
    return jsonify({"success": True, "message": "تم حفظ بيانات قسم 'معلومات عنا' بنجاح."})
# ----------------------------------------


@app.route('/api/add_barber', methods=['POST'])
@admin_required
def add_barber():
    data = request.json
    if not data.get('name') or not data.get('phone') or not data.get('image'):
        return jsonify({"success": False, "message": "الاسم، الهاتف، والصورة مطلوبة."}), 400
    
    global site_data
    if any(b['name'] == data['name'] for b in site_data['barbers']):
        return jsonify({"success": False, "message": "هذا الحلاق موجود بالفعل."}), 400
        
    new_barber = {
        "name": data['name'],
        "phone": data['phone'],
        "image": data['image'],
        "instagram": data.get('instagram', '')
    }
    site_data['barbers'].append(new_barber)
    save_data(site_data, DATA_FILE)
    return jsonify({"success": True, "message": f"تم إضافة الحلاق {data['name']} بنجاح."})

@app.route('/api/update_barber', methods=['POST'])
@admin_required
def update_barber():
    data = request.json
    old_name = data.get('old_name')
    global site_data
    
    for i, barber in enumerate(site_data['barbers']):
        if barber['name'] == old_name:
            new_name = data.get('name')
            if new_name != old_name and any(b['name'] == new_name for b in site_data['barbers']):
                 return jsonify({"success": False, "message": "الاسم الجديد موجود بالفعل لحلاق آخر."}), 400

            site_data['barbers'][i]['name'] = new_name
            site_data['barbers'][i]['phone'] = data.get('phone', barber['phone'])
            site_data['barbers'][i]['image'] = data.get('image', barber['image'])
            site_data['barbers'][i]['instagram'] = data.get('instagram', '')

            for img in site_data['gallery_images']:
                if img['barber_name'] == old_name:
                    img['barber_name'] = new_name
            
            save_data(site_data, DATA_FILE)
            return jsonify({"success": True, "message": f"تم تحديث بيانات الحلاق {new_name} بنجاح."})
    
    return jsonify({"success": False, "message": "الحلاق غير موجود."}), 404

@app.route('/api/delete_barber/<name>', methods=['DELETE'])
@admin_required
def delete_barber(name):
    global site_data
    initial_length = len(site_data['barbers'])
    site_data['barbers'] = [b for b in site_data['barbers'] if b['name'] != name]
    
    if len(site_data['barbers']) < initial_length:
        site_data['gallery_images'] = [img for img in site_data['gallery_images'] if img['barber_name'] != name]
        save_data(site_data, DATA_FILE)
        return jsonify({"success": True, "message": f"تم حذف الحلاق {name} وصوره من المعرض بنجاح."})
    
    return jsonify({"success": False, "message": "الحلاق غير موجود."}), 404

@app.route('/api/add_image', methods=['POST'])
@admin_required
def add_image():
    data = request.json
    filename = data.get('filename')
    barber_name = data.get('barber_name')
    
    if not filename or not barber_name:
        return jsonify({"success": False, "message": "اسم الملف واسم الحلاق مطلوبان."}), 400
        
    global site_data
    new_image = {"filename": filename, "barber_name": barber_name}
    site_data['gallery_images'].append(new_image)
    save_data(site_data, DATA_FILE)
    return jsonify({"success": True, "message": f"تم إضافة الصورة {filename} بنجاح."})

@app.route('/api/delete_image/<filename>', methods=['DELETE'])
@admin_required
def delete_image(filename):
    global site_data
    initial_length = len(site_data['gallery_images'])
    site_data['gallery_images'] = [img for img in site_data['gallery_images'] if img['filename'] != filename]
    
    if len(site_data['gallery_images']) < initial_length:
        save_data(site_data, DATA_FILE)
        return jsonify({"success": True, "message": f"تم حذف الصورة {filename} بنجاح."})
    
    return jsonify({"success": False, "message": "الصورة غير موجودة."}), 404

@app.route('/api/add_text', methods=['POST'])
@admin_required
def add_extra_text():
    data = request.json
    key = data.get('key')
    value = data.get('value')
    
    if not key or not value:
        return jsonify({"success": False, "message": "المفتاح والقيمة مطلوبان."}), 400
        
    global site_data
    if 'extra_texts' not in site_data:
        site_data['extra_texts'] = {}

    if key.startswith('about_') or key in ['hero_title', 'hero_desc']:
         return jsonify({"success": False, "message": "لا يمكن إضافة هذا المفتاح هنا. استخدم قسم 'معلومات عنا' أو 'النصوص الرئيسية'."}), 400

    site_data['extra_texts'][key] = value
    save_data(site_data, DATA_FILE)
    return jsonify({"success": True, "message": f"تم إضافة النص بالمفتاح {key} بنجاح."})

@app.route('/api/delete_text/<key>', methods=['DELETE'])
@admin_required
def delete_extra_text(key):
    global site_data
    if 'extra_texts' in site_data and key in site_data['extra_texts']:
        if key.startswith('about_') or key in ['hero_title', 'hero_desc']:
            return jsonify({"success": False, "message": "لا يمكن حذف هذا النص الأساسي."}), 400
            
        del site_data['extra_texts'][key]
        save_data(site_data, DATA_FILE)
        return jsonify({"success": True, "message": f"تم حذف النص بالمفتاح {key} بنجاح."})
    
    return jsonify({"success": False, "message": "النص غير موجود."}), 40
if __name__ == '__main__':
    app.run(debug=True)
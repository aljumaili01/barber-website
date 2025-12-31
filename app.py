from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = "super_secret_key"  # مفتاح ضروري لتأمين الجلسات

# بيانات افتراضية للموقع (سيتم عرضها في index.html)
site_data = {
    "hero_title": "صالون الأسد للحلاقة",
    "hero_desc": "أفضل تجربة حلاقة في المنطقة، جودة وعناية فائقة.",
    "barbers": [
    {"name": "رائد", "phone": "905011087030, "instagram": "", "image": "kuafor_raed.jpg"},
        {"name": "قاسم", "phone": "905354057831", "instagram": "https://www.instagram.com/bi9ck?igsh=MWZqdjgzaGozMTJyYg%3D%3D&utm_source=qr", "image": "kuaför_qasim.jpg"},
        {"name": "حيدر", "phone": "905383686314", "instagram": "", "image": "kuafor_hayder.jpeg"},
        {"name": "مصطفى", "phone": "905315969753", "instagram": "https://www.instagram.com/mustafa_hairdresser77?igsh=NXZqdmhyeG04YzQ3&utm_source=qr", "image": "kuafor_mustafa.jpg"}
    ],
    "gallery_images": [],
    "extra_texts": {
        "about_title": "ما يميزنا",
        "about_desc_card1": "حلاقة عصرية تناسب شخصيتك.",
        "about_image1": "صوره داخليه.jpg",
        "opening_hours": "يومياً من 9:00 صباحاً حتى 10:00 مساءً",
        "address": "اسطنبول، الفاتح، شارع الاستقلال"
    }
}

# 1. الصفحة الرئيسية (التي أرسلت كودها أنت)
@app.route('/')
def index():
    return render_template('index.html', site_data=site_data)

# 2. صفحة تسجيل دخول الإدارة (حل مشكلة Method Not Allowed)
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # يمكنك تغيير admin و 1234 حسب رغبتك
        if username == 'admin' and password == '1234':
            return redirect(url_for('dashboard'))
        else:
            return "بيانات الدخول خاطئة! <a href='/admin_login'>حاول مرة أخرى</a>"
            
    return render_template('admin_login.html')

# 3. لوحة التحكم (Dashboard)
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', site_data=site_data)

# 4. وظيفة إضافة حلاق جديد
@app.route('/add_barber', methods=['POST'])
def add_barber():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        instagram = request.form.get('instagram')
        
        # إضافة الحلاق الجديد للقائمة
        new_barber = {
            "name": name,
            "phone": phone,
            "instagram": instagram,
            "image": "kuafor_mustafa.jpg" # صورة افتراضية
        }
        
        site_data['barbers'].append(new_barber)
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)

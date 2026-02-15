from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(
    app,
    supports_credentials=True,
    origins=["http://127.0.0.1:5000"]
)

# تكوين رفع الملفات
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'dcm'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# إنشاء مجلد الرفع إذا لم يكن موجوداً
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# تكوين قاعدة البيانات
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '1234',  # ضع كلمة المرور هنا
    'database': 'medical_records',
    'port': '3306'
}

# دالة للاتصال بقاعدة البيانات
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"خطأ في الاتصال بقاعدة البيانات: {e}")
        return None

# دالة للتحقق من امتداد الملف
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# الصفحة الرئيسية - تسجيل الدخول
@app.route('/')
def index():
    return render_template('index.html')

# صفحة المريض
@app.route('/patient')
def patient():
    if 'user_id' not in session or session.get('role') != 'patient':
        return redirect(url_for('index'))
    return render_template('patient.html')

# صفحة الدكتور
@app.route('/doctor')
def doctor():
    if 'user_id' not in session or session.get('role') != 'doctor':
        return redirect(url_for('index'))
    return render_template('doctor.html')

# API: تسجيل مستخدم جديد
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')  # 'patient' or 'doctor'
    age = data.get('age')
    phone = data.get('phone')
    
    if not all([name, email, password, role]):
        return jsonify({'success': False, 'message': 'يرجى ملء جميع الحقول المطلوبة'}), 400
    
    # التحقق من صحة الدور
    if role not in ['patient', 'doctor']:
        return jsonify({'success': False, 'message': 'نوع المستخدم غير صحيح'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'خطأ في الاتصال بقاعدة البيانات'}), 500
    
    cursor = conn.cursor()
    
    try:
        # التحقق من وجود البريد الإلكتروني
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'البريد الإلكتروني مسجل بالفعل'}), 400
        
        # تشفير كلمة المرور
        hashed_password = generate_password_hash(password)
        
        # إدراج المستخدم الجديد
        query = """
            INSERT INTO users (name, email, password, role, age, phone, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, email, hashed_password, role, age, phone, datetime.now()))
        conn.commit()
        
        return jsonify({'success': True, 'message': 'تم التسجيل بنجاح'}), 201
        
    except Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'خطأ في التسجيل: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

# API: تسجيل الدخول
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    
    if not all([email, password, role]):
        return jsonify({'success': False, 'message': 'يرجى ملء جميع الحقول'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'خطأ في الاتصال بقاعدة البيانات'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s AND role = %s", (email, role))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['email'] = user['email']
            session['role'] = user['role']
            
            return jsonify({
                'success': True,
                'message': 'تم تسجيل الدخول بنجاح',
                'user': {
                    'id': user['id'],
                    'name': user['name'],
                    'email': user['email'],
                    'role': user['role']
                }
            }), 200
        else:
            return jsonify({'success': False, 'message': 'البريد الإلكتروني أو كلمة المرور غير صحيحة'}), 401
            
    except Error as e:
        return jsonify({'success': False, 'message': f'خطأ في تسجيل الدخول: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

# API: تسجيل الخروج
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'تم تسجيل الخروج بنجاح'}), 200

# API: رفع مستند طبي (للمريض)
@app.route('/api/upload-document', methods=['POST'])
def upload_document():
    if 'user_id' not in session or session.get('role') != 'patient':
        return jsonify({'success': False, 'message': 'غير مصرح'}), 401
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'لم يتم اختيار ملف'}), 400
    
    file = request.files['file']
    document_type = request.form.get('document_type')
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'لم يتم اختيار ملف'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'نوع الملف غير مسموح'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'خطأ في الاتصال بقاعدة البيانات'}), 500
    
    cursor = conn.cursor()
    
    try:
        # إنشاء مجلد خاص بالمريض
        patient_folder = os.path.join(app.config['UPLOAD_FOLDER'], f"patient_{session['user_id']}")
        if not os.path.exists(patient_folder):
            os.makedirs(patient_folder)
        
        # حفظ الملف
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        
        # المسار الكامل للملف
        filepath = os.path.join(patient_folder, unique_filename)
        file.save(filepath)
        
        # المسار النسبي للحفظ في قاعدة البيانات
        db_filepath = f"patient_{session['user_id']}/{unique_filename}"
        
        # حفظ المعلومات في قاعدة البيانات
        query = """
            INSERT INTO medical_documents (patient_id, document_type, file_name, file_path, upload_date)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (session['user_id'], document_type, filename, db_filepath, datetime.now()))
        conn.commit()
        
        document_id = cursor.lastrowid
        
        return jsonify({
            'success': True,
            'message': 'تم رفع المستند بنجاح',
            'document': {
                'id': document_id,
                'name': filename,
                'type': document_type,
                'date': datetime.now().strftime('%Y-%m-%d')
            }
        }), 201
        
    except Error as e:
        conn.rollback()
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'success': False, 'message': f'خطأ في رفع المستند: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

# API: عرض مستندات المريض
@app.route('/api/my-documents', methods=['GET'])
def get_my_documents():
    if 'user_id' not in session or session.get('role') != 'patient':
        return jsonify({'success': False, 'message': 'غير مصرح'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'خطأ في الاتصال بقاعدة البيانات'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
            SELECT id, document_type, file_name, upload_date
            FROM medical_documents
            WHERE patient_id = %s
            ORDER BY upload_date DESC
        """
        cursor.execute(query, (session['user_id'],))
        documents = cursor.fetchall()
        
        # تنسيق التواريخ
        for doc in documents:
            doc['upload_date'] = doc['upload_date'].strftime('%Y-%m-%d')
        
        return jsonify({'success': True, 'documents': documents}), 200
        
    except Error as e:
        return jsonify({'success': False, 'message': f'خطأ في جلب المستندات: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

# API: إحصائيات المستندات للمريض
@app.route('/api/document-stats', methods=['GET'])
def get_document_stats():
    if 'user_id' not in session or session.get('role') != 'patient':
        return jsonify({'success': False, 'message': 'غير مصرح'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'خطأ في الاتصال بقاعدة البيانات'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
            SELECT document_type, COUNT(*) as count
            FROM medical_documents
            WHERE patient_id = %s
            GROUP BY document_type
        """
        cursor.execute(query, (session['user_id'],))
        stats = cursor.fetchall()
        
        # تحويل النتائج إلى قاموس
        stats_dict = {row['document_type']: row['count'] for row in stats}
        
        # حساب الإجمالي
        cursor.execute("SELECT COUNT(*) as total FROM medical_documents WHERE patient_id = %s", (session['user_id'],))
        total = cursor.fetchone()['total']
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'lab_results': stats_dict.get('نتائج التحاليل', 0),
                'imaging': stats_dict.get('الأشعة (X-Ray, MRI, CT)', 0),
                'prescriptions': stats_dict.get('الوصفات الطبية', 0),
                'reports': stats_dict.get('التقارير الطبية', 0),
                'other': stats_dict.get('مستندات أخرى', 0)
            }
        }), 200
        
    except Error as e:
        return jsonify({'success': False, 'message': f'خطأ في جلب الإحصائيات: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

# API: عرض قائمة المرضى (للدكتور)
@app.route('/api/patients', methods=['GET'])
def get_patients():
    if 'user_id' not in session or session.get('role') != 'doctor':
        return jsonify({'success': False, 'message': 'غير مصرح'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'خطأ في الاتصال بقاعدة البيانات'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
            SELECT DISTINCT u.id, u.name, u.email, u.age, u.phone,
                   (SELECT COUNT(*) FROM medical_documents WHERE patient_id = u.id) as document_count,
                   (SELECT MAX(upload_date) FROM medical_documents WHERE patient_id = u.id) as last_visit
            FROM users u
            INNER JOIN doctor_patient_access dpa ON u.id = dpa.patient_id
            WHERE dpa.doctor_id = %s AND u.role = 'patient'
            ORDER BY last_visit DESC
        """
        cursor.execute(query, (session['user_id'],))
        patients = cursor.fetchall()
        
        # تنسيق التواريخ
        for patient in patients:
            if patient['last_visit']:
                patient['last_visit'] = patient['last_visit'].strftime('%Y-%m-%d')
        
        return jsonify({'success': True, 'patients': patients}), 200
        
    except Error as e:
        return jsonify({'success': False, 'message': f'خطأ في جلب المرضى: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

# API: عرض مستندات مريض معين (للدكتور)
@app.route('/api/patient-documents/<int:patient_id>', methods=['GET'])
def get_patient_documents(patient_id):
    if 'user_id' not in session or session.get('role') != 'doctor':
        return jsonify({'success': False, 'message': 'غير مصرح'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'خطأ في الاتصال بقاعدة البيانات'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # التحقق من وجود صلاحية
        cursor.execute("""
            SELECT * FROM doctor_patient_access
            WHERE doctor_id = %s AND patient_id = %s
        """, (session['user_id'], patient_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'ليس لديك صلاحية لعرض مستندات هذا المريض'}), 403
        
        # جلب المستندات
        query = """
            SELECT id, document_type, file_name, upload_date
            FROM medical_documents
            WHERE patient_id = %s
            ORDER BY upload_date DESC
        """
        cursor.execute(query, (patient_id,))
        documents = cursor.fetchall()
        
        # تنسيق التواريخ
        for doc in documents:
            doc['upload_date'] = doc['upload_date'].strftime('%Y-%m-%d')
        
        return jsonify({'success': True, 'documents': documents}), 200
        
    except Error as e:
        return jsonify({'success': False, 'message': f'خطأ في جلب المستندات: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

# API: إعطاء صلاحية لدكتور (المريض يدي إذن)
@app.route('/api/grant-access', methods=['POST'])
def grant_access():
    if 'user_id' not in session or session.get('role') != 'patient':
        return jsonify({'success': False, 'message': 'غير مصرح'}), 401
    
    data = request.get_json()
    doctor_email = data.get('doctor_email')
    
    if not doctor_email:
        return jsonify({'success': False, 'message': 'يرجى إدخال البريد الإلكتروني للدكتور'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'خطأ في الاتصال بقاعدة البيانات'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # البحث عن الدكتور
        cursor.execute("SELECT id FROM users WHERE email = %s AND role = 'doctor'", (doctor_email,))
        doctor = cursor.fetchone()
        
        if not doctor:
            return jsonify({'success': False, 'message': 'الدكتور غير موجود'}), 404
        
        # التحقق من وجود الصلاحية مسبقاً
        cursor.execute("""
            SELECT * FROM doctor_patient_access
            WHERE doctor_id = %s AND patient_id = %s
        """, (doctor['id'], session['user_id']))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'تم منح الصلاحية لهذا الدكتور مسبقاً'}), 400
        
        # إضافة الصلاحية
        query = """
            INSERT INTO doctor_patient_access (doctor_id, patient_id, granted_date)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (doctor['id'], session['user_id'], datetime.now()))
        conn.commit()
        
        return jsonify({'success': True, 'message': 'تم منح الصلاحية للدكتور بنجاح'}), 201
        
    except Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'خطأ في منح الصلاحية: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

# API: إحصائيات الدكتور
@app.route('/api/doctor-stats', methods=['GET'])
def get_doctor_stats():
    if 'user_id' not in session or session.get('role') != 'doctor':
        return jsonify({'success': False, 'message': 'غير مصرح'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'خطأ في الاتصال بقاعدة البيانات'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # عدد المرضى
        cursor.execute("""
            SELECT COUNT(DISTINCT patient_id) as patient_count
            FROM doctor_patient_access
            WHERE doctor_id = %s
        """, (session['user_id'],))
        patient_count = cursor.fetchone()['patient_count']
        
        # إجمالي الملفات
        cursor.execute("""
            SELECT COUNT(md.id) as total_documents
            FROM medical_documents md
            INNER JOIN doctor_patient_access dpa ON md.patient_id = dpa.patient_id
            WHERE dpa.doctor_id = %s
        """, (session['user_id'],))
        total_documents = cursor.fetchone()['total_documents']
        
        # الملفات المرفوعة اليوم
        cursor.execute("""
            SELECT COUNT(md.id) as today_documents
            FROM medical_documents md
            INNER JOIN doctor_patient_access dpa ON md.patient_id = dpa.patient_id
            WHERE dpa.doctor_id = %s AND DATE(md.upload_date) = CURDATE()
        """, (session['user_id'],))
        today_documents = cursor.fetchone()['today_documents']
        
        return jsonify({
            'success': True,
            'stats': {
                'patient_count': patient_count,
                'total_documents': total_documents,
                'today_documents': today_documents
            }
        }), 200
        
    except Error as e:
        return jsonify({'success': False, 'message': f'خطأ في جلب الإحصائيات: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()
# API: حذف مستند طبي (للمريض)
@app.route('/api/delete-document/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    if 'user_id' not in session or session.get('role') != 'patient':
        return jsonify({'success': False, 'message': 'غير مصرح'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'خطأ في الاتصال بقاعدة البيانات'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # التحقق من أن المستند يخص المستخدم الحالي
        cursor.execute("""
            SELECT file_path FROM medical_documents
            WHERE id = %s AND patient_id = %s
        """, (document_id, session['user_id']))
        
        document = cursor.fetchone()
        
        if not document:
            return jsonify({'success': False, 'message': 'المستند غير موجود'}), 404
        
        # حذف الملف من النظام
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], document['file_path'])
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # حذف السجل من قاعدة البيانات
        cursor.execute("DELETE FROM medical_documents WHERE id = %s", (document_id,))
        conn.commit()
        
        return jsonify({'success': True, 'message': 'تم حذف المستند بنجاح'}), 200
        
    except Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'خطأ في حذف المستند: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()
# تحميل ملف
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# API: إضافة ملاحظة من الدكتور للمريض
@app.route('/api/add-note', methods=['POST'])
def add_note():
    if 'user_id' not in session or session.get('role') != 'doctor':
        return jsonify({'success': False, 'message': 'غير مصرح'}), 401
    
    data = request.get_json()
    patient_id = data.get('patient_id')
    note_text = data.get('note_text')
    
    if not patient_id or not note_text:
        return jsonify({'success': False, 'message': 'يرجى ملء جميع الحقول'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'خطأ في الاتصال بقاعدة البيانات'}), 500
    
    cursor = conn.cursor()
    
    try:
        # التحقق من وجود صلاحية
        cursor.execute("""
            SELECT * FROM doctor_patient_access
            WHERE doctor_id = %s AND patient_id = %s
        """, (session['user_id'], patient_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'ليس لديك صلاحية لإضافة ملاحظات لهذا المريض'}), 403
        
        # إضافة الملاحظة
        query = """
            INSERT INTO doctor_notes (doctor_id, patient_id, note_text, created_at)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (session['user_id'], patient_id, note_text, datetime.now()))
        conn.commit()
        
        return jsonify({'success': True, 'message': 'تم إضافة الملاحظة بنجاح'}), 201
        
    except Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'خطأ في إضافة الملاحظة: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

# API: عرض ملاحظات المريض
@app.route('/api/my-notes', methods=['GET'])
def get_my_notes():
    if 'user_id' not in session or session.get('role') != 'patient':
        return jsonify({'success': False, 'message': 'غير مصرح'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'خطأ في الاتصال بقاعدة البيانات'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
            SELECT dn.id, dn.note_text, dn.created_at, dn.is_read, u.name as doctor_name
            FROM doctor_notes dn
            INNER JOIN users u ON dn.doctor_id = u.id
            WHERE dn.patient_id = %s
            ORDER BY dn.created_at DESC
        """
        cursor.execute(query, (session['user_id'],))
        notes = cursor.fetchall()
        
        # تنسيق التواريخ
        for note in notes:
            note['created_at'] = note['created_at'].strftime('%Y-%m-%d %H:%M')
            note['is_read'] = bool(note['is_read'])
        
        return jsonify({'success': True, 'notes': notes}), 200
        
    except Error as e:
        return jsonify({'success': False, 'message': f'خطأ في جلب الملاحظات: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

# API: عدد الملاحظات غير المقروءة
@app.route('/api/unread-notes-count', methods=['GET'])
def get_unread_notes_count():
    if 'user_id' not in session or session.get('role') != 'patient':
        return jsonify({'success': False, 'message': 'غير مصرح'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'خطأ في الاتصال بقاعدة البيانات'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM doctor_notes
            WHERE patient_id = %s AND is_read = FALSE
        """, (session['user_id'],))
        
        count = cursor.fetchone()['count']
        
        return jsonify({'success': True, 'count': count}), 200
        
    except Error as e:
        return jsonify({'success': False, 'message': f'خطأ: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

# API: تعليم الملاحظة كمقروءة
@app.route('/api/mark-note-read/<int:note_id>', methods=['POST'])
def mark_note_read(note_id):
    if 'user_id' not in session or session.get('role') != 'patient':
        return jsonify({'success': False, 'message': 'غير مصرح'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'خطأ في الاتصال بقاعدة البيانات'}), 500
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE doctor_notes
            SET is_read = TRUE
            WHERE id = %s AND patient_id = %s
        """, (note_id, session['user_id']))
        
        conn.commit()
        
        return jsonify({'success': True, 'message': 'تم التعليم كمقروء'}), 200
        
    except Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'خطأ: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

# API: عرض ملف
@app.route('/view-document/<int:document_id>')
def view_document(document_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    if not conn:
        return "خطأ في الاتصال بقاعدة البيانات", 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # التحقق من الصلاحية
        if session.get('role') == 'patient':
            # المريض يشوف ملفاته فقط
            cursor.execute("""
                SELECT file_path, file_name FROM medical_documents
                WHERE id = %s AND patient_id = %s
            """, (document_id, session['user_id']))
        elif session.get('role') == 'doctor':
            # الدكتور يشوف ملفات المرضى المصرح له بهم
            cursor.execute("""
                SELECT md.file_path, md.file_name FROM medical_documents md
                INNER JOIN doctor_patient_access dpa ON md.patient_id = dpa.patient_id
                WHERE md.id = %s AND dpa.doctor_id = %s
            """, (document_id, session['user_id']))
        else:
            return "غير مصرح", 403
        
        document = cursor.fetchone()
        
        if not document:
            return "الملف غير موجود أو ليس لديك صلاحية", 404
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], document['file_path'])
        
        if not os.path.exists(file_path):
            return "الملف غير موجود على السيرفر", 404
        
        # إرجاع الملف
        return send_from_directory(
            os.path.dirname(file_path),
            os.path.basename(file_path),
            as_attachment=False  # عرض في المتصفح بدل التحميل
        )
        
    except Error as e:
        return f"خطأ: {str(e)}", 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
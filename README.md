# مشروع دوسيه - نظام السجلات الطبية

## 📋 وصف المشروع
نظام متكامل لإدارة السجلات الطبية يسمح للمرضى برفع ملفاتهم الطبية والدكاترة بالوصول إليها بعد الحصول على إذن.

## 🏗️ هيكل المشروع

```
medical-records-system/
│
├── app.py                      # Flask Backend (الخادم الرئيسي)
├── requirements.txt            # المكتبات المطلوبة
├── database.sql               # ملف قاعدة البيانات
│
├── templates/                 # صفحات HTML
│   ├── index.html            # صفحة تسجيل الدخول
│   ├── patient.html          # صفحة المريض
│   └── doctor.html           # صفحة الدكتور
│
├── static/                    # الملفات الثابتة
│   ├── style.css             # ملف التنسيقات
│   └── main.js               # ملف JavaScript
│
└── uploads/                   # مجلد تخزين الملفات المرفوعة (يُنشأ تلقائياً)
```

## 🚀 خطوات التشغيل

### 1. تثبيت Python
تأكد من تثبيت Python 3.8 أو أحدث على جهازك.

### 2. تثبيت MySQL
- حمّل وثبّت [MySQL Community Server](https://dev.mysql.com/downloads/mysql/)
- شغّل خدمة MySQL

### 3. إعداد قاعدة البيانات

افتح MySQL Command Line أو MySQL Workbench وشغّل الأوامر التالية:

```sql
-- إنشاء قاعدة البيانات
CREATE DATABASE medical_records CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- استخدام قاعدة البيانات
USE medical_records;

-- شغّل باقي أوامر SQL من ملف database.sql
```

أو شغّل الملف مباشرة:
```bash
mysql -u root -p < database.sql
```

### 4. تثبيت المكتبات المطلوبة

```bash
# إنشاء بيئة افتراضية (اختياري لكن مُفضّل)
python -m venv venv

# تفعيل البيئة الافتراضية
# على Windows:
venv\Scripts\activate
# على Mac/Linux:
source venv/bin/activate

# تثبيت المكتبات
pip install -r requirements.txt
```

### 5. تعديل إعدادات قاعدة البيانات

افتح ملف `app.py` وعدّل إعدادات الاتصال بقاعدة البيانات:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'كلمة_المرور_بتاعتك',  # ضع كلمة مرور MySQL هنا
    'database': 'medical_records'
}
```

### 6. تشغيل المشروع

```bash
python app.py
```

المشروع هيشتغل على: `http://localhost:5000`

## 👤 بيانات الدخول التجريبية

### مريض:
- **البريد الإلكتروني:** patient1@test.com
- **كلمة المرور:** password123

### دكتور:
- **البريد الإلكتروني:** doctor1@test.com
- **كلمة المرور:** password123

## 🔧 الوظائف المتاحة

### للمريض:
✅ تسجيل دخول/تسجيل حساب جديد
✅ رفع المستندات الطبية (أشعة، تحاليل، روشتات، إلخ)
✅ عرض المستندات الشخصية
✅ إحصائيات المستندات
✅ إعطاء صلاحية للدكتور للوصول للملفات

### للدكتور:
✅ تسجيل دخول/تسجيل حساب جديد
✅ عرض قائمة المرضى
✅ عرض مستندات المرضى المصرح له بالوصول إليهم
✅ إحصائيات المرضى والملفات
✅ البحث عن المرضى

## 🗄️ قاعدة البيانات

### الجداول:

**1. users** - جدول المستخدمين
- id: المعرّف الفريد
- name: الاسم
- email: البريد الإلكتروني
- password: كلمة المرور (مُشفّرة)
- role: الدور (patient/doctor)
- age: العمر
- phone: رقم الهاتف

**2. medical_documents** - جدول المستندات الطبية
- id: المعرّف الفريد
- patient_id: معرّف المريض
- document_type: نوع المستند
- file_name: اسم الملف
- file_path: مسار الملف
- upload_date: تاريخ الرفع

**3. doctor_patient_access** - جدول صلاحيات الوصول
- id: المعرّف الفريد
- doctor_id: معرّف الدكتور
- patient_id: معرّف المريض
- granted_date: تاريخ منح الصلاحية

## 📡 API Endpoints

### Authentication
- `POST /api/register` - تسجيل مستخدم جديد
- `POST /api/login` - تسجيل الدخول
- `POST /api/logout` - تسجيل الخروج

### Patient APIs
- `POST /api/upload-document` - رفع مستند طبي
- `GET /api/my-documents` - عرض مستنداتي
- `GET /api/document-stats` - إحصائيات المستندات
- `POST /api/grant-access` - إعطاء صلاحية لدكتور

### Doctor APIs
- `GET /api/patients` - عرض قائمة المرضى
- `GET /api/patient-documents/<patient_id>` - عرض مستندات مريض
- `GET /api/doctor-stats` - إحصائيات الدكتور

## 🔐 الأمان

- ✅ كلمات المرور مُشفّرة باستخدام `werkzeug.security`
- ✅ نظام sessions للمصادقة
- ✅ التحقق من صلاحيات الوصول
- ✅ التحقق من أنواع الملفات المرفوعة
- ✅ حماية من SQL Injection

## 📝 ملاحظات مهمة

1. **حجم الملفات:** الحد الأقصى للملف الواحد 10 ميجابايت
2. **أنواع الملفات المسموحة:** PDF, JPG, PNG, DICOM
3. **الترميز:** UTF-8 للدعم الكامل للغة العربية
4. **الـ Session:** تنتهي عند إغلاق المتصفح

## 🐛 حل المشاكل الشائعة

### مشكلة الاتصال بـ MySQL
```bash
# تأكد من تشغيل خدمة MySQL
# Windows:
net start MySQL80

# Linux/Mac:
sudo systemctl start mysql
```

### مشكلة تثبيت mysql-connector-python
```bash
pip install mysql-connector-python --upgrade
```

### خطأ في رفع الملفات
- تأكد من وجود مجلد `uploads/`
- تأكد من صلاحيات الكتابة على المجلد

## 📧 التواصل والدعم

لأي استفسارات أو مشاكل، يمكنك:
- فتح issue على GitHub
- مراجعة الكود والتعليقات
- التواصل مع المطور

---

**ملحوظة:** هذا مشروع تعليمي. للاستخدام في بيئة إنتاجية حقيقية، يُنصح بإضافة:
- HTTPS
- Rate limiting
- Database connection pooling
- Better error handling
- Logging system
- File virus scanning
- Backup system
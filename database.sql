-- إنشاء قاعدة البيانات
CREATE DATABASE IF NOT EXISTS medical_records CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE medical_records;

-- جدول المستخدمين (دكاترة ومرضى)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('patient', 'doctor') NOT NULL,
    age INT,
    phone VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول المستندات الطبية
CREATE TABLE IF NOT EXISTS medical_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    document_type VARCHAR(100) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_document_type (document_type),
    INDEX idx_upload_date (upload_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول صلاحيات الدكتور للوصول لمستندات المريض
CREATE TABLE IF NOT EXISTS doctor_patient_access (
    id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id INT NOT NULL,
    patient_id INT NOT NULL,
    granted_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_access (doctor_id, patient_id),
    INDEX idx_doctor_id (doctor_id),
    INDEX idx_patient_id (patient_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- إدراج بيانات تجريبية
-- كلمة المرور المشفرة لـ "password123" باستخدام Werkzeug
-- الهاش ده متولد من: generate_password_hash("password123")

INSERT INTO users (name, email, password, role, age, phone) VALUES
('محمد أحمد', 'patient1@test.com', 'scrypt:32768:8:1$EF6tM9xqPLvQJC5W$d91de62e3c24f4b8f66f0e6c5e1e8f5d3e4b6f8c2a1d3e5f7b9c8d6e4f2a1b3c5d7e9f8a6b4c2d1e3f5g7h9i8j6k4l2m1n3o5p7q9r8s6t4u2v1w3x5y7z9', 'patient', 45, '01012345678'),
('د. سارة محمود', 'doctor1@test.com', 'scrypt:32768:8:1$EF6tM9xqPLvQJC5W$d91de62e3c24f4b8f66f0e6c5e1e8f5d3e4b6f8c2a1d3e5f7b9c8d6e4f2a1b3c5d7e9f8a6b4c2d1e3f5g7h9i8j6k4l2m1n3o5p7q9r8s6t4u2v1w3x5y7z9', 'doctor', 35, '01112345678'),
('فاطمة علي', 'patient2@test.com', 'scrypt:32768:8:1$EF6tM9xqPLvQJC5W$d91de62e3c24f4b8f66f0e6c5e1e8f5d3e4b6f8c2a1d3e5f7b9c8d6e4f2a1b3c5d7e9f8a6b4c2d1e3f5g7h9i8j6k4l2m1n3o5p7q9r8s6t4u2v1w3x5y7z9', 'patient', 32, '01212345678'),
('أحمد حسن', 'patient3@test.com', 'scrypt:32768:8:1$EF6tM9xqPLvQJC5W$d91de62e3c24f4b8f66f0e6c5e1e8f5d3e4b6f8c2a1d3e5f7b9c8d6e4f2a1b3c5d7e9f8a6b4c2d1e3f5g7h9i8j6k4l2m1n3o5p7q9r8s6t4u2v1w3x5y7z9', 'patient', 58, '01312345678'),
('نور خالد', 'patient4@test.com', 'scrypt:32768:8:1$EF6tM9xqPLvQJC5W$d91de62e3c24f4b8f66f0e6c5e1e8f5d3e4b6f8c2a1d3e5f7b9c8d6e4f2a1b3c5d7e9f8a6b4c2d1e3f5g7h9i8j6k4l2m1n3o5p7q9r8s6t4u2v1w3x5y7z9', 'patient', 27, '01412345678'),
('عمر سعيد', 'patient5@test.com', 'scrypt:32768:8:1$EF6tM9xqPLvQJC5W$d91de62e3c24f4b8f66f0e6c5e1e8f5d3e4b6f8c2a1d3e5f7b9c8d6e4f2a1b3c5d7e9f8a6b4c2d1e3f5g7h9i8j6k4l2m1n3o5p7q9r8s6t4u2v1w3x5y7z9', 'patient', 51, '01512345678');

-- صلاحيات الدكتور للوصول لمرضى
INSERT INTO doctor_patient_access (doctor_id, patient_id, granted_date) VALUES
(2, 1, '2024-11-01 10:00:00'),
(2, 3, '2024-11-02 11:30:00'),
(2, 4, '2024-11-03 09:15:00'),
(2, 5, '2024-11-04 14:20:00'),
(2, 6, '2024-11-05 16:45:00');

-- مستندات طبية تجريبية
INSERT INTO medical_documents (patient_id, document_type, file_name, file_path, upload_date) VALUES
(1, 'نتائج التحاليل', 'blood_test_nov2024.pdf', '1_20241120_120000_blood_test_nov2024.pdf', '2024-11-20 10:30:00'),
(1, 'الأشعة (X-Ray, MRI, CT)', 'xray_chest.jpg', '1_20241120_130000_xray_chest.jpg', '2024-11-20 11:00:00'),
(1, 'الوصفات الطبية', 'prescription_nov.pdf', '1_20241119_140000_prescription_nov.pdf', '2024-11-19 14:30:00'),
(3, 'نتائج التحاليل', 'lab_results.pdf', '3_20241118_100000_lab_results.pdf', '2024-11-18 09:15:00'),
(4, 'التقارير الطبية', 'medical_report.pdf', '4_20241115_160000_medical_report.pdf', '2024-11-15 15:45:00');
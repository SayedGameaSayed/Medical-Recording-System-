from werkzeug.security import generate_password_hash

# توليد كلمة مرور مشفرة واحدة لكل المستخدمين
password = "password123"
hashed = generate_password_hash(password)

print(f"كلمة المرور الأصلية: {password}")
print(f"كلمة المرور المشفرة:")
print(hashed)
print("\n" + "="*50)
print("استخدم الـ UPDATE command ده في MySQL:")
print("="*50)

users = [
    ('patient1@test.com', 'محمد أحمد'),
    ('doctor1@test.com', 'د. سارة محمود'),
    ('patient2@test.com', ' فاطمة علي'),
    ('patient3@test.com', 'أحمد حسن'),
    ('patient4@test.com', 'نور خالد'),
    ('patient5@test.com', 'عمر سعيد')
]

print("\n-- Update passwords for all users")
for email, name in users:
    print(f"UPDATE users SET password = '{hashed}' WHERE email = '{email}';")
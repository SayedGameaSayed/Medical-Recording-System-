# Dossier — Medical Records Management System

A full-stack web application that enables patients to securely upload and manage their medical records, and allows authorized doctors to access them with patient consent.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Demo Credentials](#demo-credentials)
- [Features](#features)
- [Database Schema](#database-schema)
- [API Reference](#api-reference)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Production Considerations](#production-considerations)

---

## Project Structure

```
medical-records-system/
│
├── app.py                  # Main Flask backend
├── requirements.txt        # Python dependencies
├── database.sql            # Database schema & seed data
│
├── templates/
│   ├── index.html          # Login page
│   ├── patient.html        # Patient dashboard
│   └── doctor.html         # Doctor dashboard
│
├── static/
│   ├── style.css           # Stylesheet
│   └── main.js             # Frontend scripts
│
└── uploads/                # Uploaded files (auto-created at runtime)
```

---

## Prerequisites

- Python 3.8+
- MySQL Community Server

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/medical-records-system.git
cd medical-records-system
```

### 2. Set up a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up the database

Ensure MySQL is running, then execute:

```bash
mysql -u root -p < database.sql
```

Or manually run the following in your MySQL client:

```sql
CREATE DATABASE medical_records CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE medical_records;
-- Then run the remaining statements from database.sql
```

### 5. Configure the application

Open `app.py` and update the database connection settings:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_mysql_password',
    'database': 'medical_records'
}
```

### 6. Run the application

```bash
python app.py
```

The application will be available at `http://localhost:5000`.

---

## Demo Credentials

| Role    | Email               | Password    |
|---------|---------------------|-------------|
| Patient | patient1@test.com   | password123 |
| Doctor  | doctor1@test.com    | password123 |

---

## Features

### Patient
- Register and log in
- Upload medical documents (scans, lab results, prescriptions, etc.)
- View personal documents
- View document statistics
- Grant specific doctors access to records

<img width="757" height="455" alt="image" src="https://github.com/user-attachments/assets/057ac25e-a7ac-4101-b2b4-6e9961ddfbf1" />

### Doctor
- Register and log in
- View list of authorized patients
- Access documents for permitted patients
- View patient and file statistics
- Search for patients

---

## Database Schema

### `users`
| Column   | Type    | Description                  |
|----------|---------|------------------------------|
| id       | INT     | Primary key                  |
| name     | VARCHAR | Full name                    |
| email    | VARCHAR | Email address                |
| password | VARCHAR | Hashed password              |
| role     | ENUM    | `patient` or `doctor`        |
| age      | INT     | Age                          |
| phone    | VARCHAR | Phone number                 |

### `medical_documents`
| Column        | Type     | Description         |
|---------------|----------|---------------------|
| id            | INT      | Primary key         |
| patient_id    | INT      | Reference to user   |
| document_type | VARCHAR  | Type of document    |
| file_name     | VARCHAR  | Original file name  |
| file_path     | VARCHAR  | Storage path        |
| upload_date   | DATETIME | Upload timestamp    |

### `doctor_patient_access`
| Column       | Type     | Description              |
|--------------|----------|--------------------------|
| id           | INT      | Primary key              |
| doctor_id    | INT      | Reference to doctor user |
| patient_id   | INT      | Reference to patient     |
| granted_date | DATETIME | Access grant timestamp   |

---

## API Reference

### Authentication

| Method | Endpoint       | Description          |
|--------|----------------|----------------------|
| POST   | /api/register  | Register a new user  |
| POST   | /api/login     | Log in               |
| POST   | /api/logout    | Log out              |

### Patient Endpoints

| Method | Endpoint              | Description                     |
|--------|-----------------------|---------------------------------|
| POST   | /api/upload-document  | Upload a medical document       |
| GET    | /api/my-documents     | Retrieve own documents          |
| GET    | /api/document-stats   | Get document statistics         |
| POST   | /api/grant-access     | Grant a doctor access           |

### Doctor Endpoints

| Method | Endpoint                           | Description                        |
|--------|------------------------------------|------------------------------------|
| GET    | /api/patients                      | List authorized patients           |
| GET    | /api/patient-documents/<patient_id>| Get a patient's documents          |
| GET    | /api/doctor-stats                  | Get doctor statistics              |

---

## Security

- Passwords are hashed using `werkzeug.security`
- Session-based authentication
- Role-based access control on all endpoints
- File type validation on upload
- Protection against SQL injection via parameterized queries

**File upload limits:**
- Maximum file size: **10 MB**
- Allowed formats: `PDF`, `JPG`, `PNG`, `DICOM`

---

## Troubleshooting

**MySQL service not running**

```bash
# Windows
net start MySQL80

# macOS / Linux
sudo systemctl start mysql
```

**`mysql-connector-python` installation fails**

```bash
pip install mysql-connector-python --upgrade
```

**File upload errors**

- Confirm the `uploads/` directory exists at the project root
- Confirm the directory has write permissions

---

## Production Considerations

This project is intended for educational purposes. Before deploying to a production environment, the following should be addressed:

- Enable HTTPS (TLS/SSL)
- Implement rate limiting
- Add database connection pooling
- Improve error handling and logging
- Integrate file virus scanning
- Set up automated database backups
- Use environment variables for all secrets (never hardcode credentials)

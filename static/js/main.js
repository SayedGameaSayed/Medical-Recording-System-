// Theme Management - استخدام متغير عادي بدل localStorage
let isDarkMode = false;
let selectedRole = 'patient';
let uploadedFiles = [];

// API Base URL
const API_BASE = 'http://127.0.0.1:5000/api';


// Initialize theme on page load
document.addEventListener('DOMContentLoaded', function() {
    // Setup file upload listeners if on patient page
    setupFileUpload();
    
    // Load data based on page
    if (document.body.classList.contains('patient-page')) {
        loadPatientData();
    } else if (document.body.classList.contains('doctor-page')) {
        loadDoctorData();
    }
});

// Toggle theme
function toggleTheme() {
    isDarkMode = !isDarkMode;
    document.body.classList.toggle('dark-mode');
    updateThemeIcon();
}

function updateThemeIcon() {
    const icons = document.querySelectorAll('.theme-icon');
    icons.forEach(icon => {
        icon.textContent = isDarkMode ? '☀️' : '🌙';
    });
}

// Login functionality
function selectRole(role) {
    selectedRole = role;
    document.querySelectorAll('.role-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-role="${role}"]`).classList.add('active');
}

async function handleLogin() {
    const email = document.querySelector('input[type="email"]').value;
    const password = document.querySelector('input[type="password"]').value;
    
    if (!email || !password) {
        alert('يرجى ملء جميع الحقول');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                email: email,
                password: password,
                role: selectedRole
            })
        });
        
        const data = await response.json();
        
        console.log('Login response:', data); // للتشخيص
        
        if (data.success) {
            // Redirect based on role
            if (selectedRole === 'patient') {
                window.location.href = '/patient';
            } else {
                window.location.href = '/doctor';
            }
        } else {
            alert(data.message || 'حدث خطأ في تسجيل الدخول');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('حدث خطأ في الاتصال بالخادم');
    }
}

async function handleLogout() {
    try {
        await fetch(`${API_BASE}/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        window.location.href = '/';
    } catch (error) {
        console.error('Error:', error);
        window.location.href = '/';
    }
}

// Alert functionality
function closeAlert(alertId) {
    document.getElementById(alertId).style.display = 'none';
}

// File upload functionality
function setupFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    if (!uploadArea || !fileInput) return;
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        handleFiles(e.dataTransfer.files);
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });
}

async function handleFiles(files) {
    const docType = document.getElementById('docType').value;
    const fileList = document.getElementById('fileList');
    const uploadedFilesDiv = document.getElementById('uploadedFiles');
    
    for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('document_type', docType);
        
        try {
            const response = await fetch(`${API_BASE}/upload-document`, {
                method: 'POST',
                credentials: 'include',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                const fileObj = {
                    id: data.document.id,
                    name: data.document.name,
                    size: (file.size / 1024).toFixed(2),
                    type: data.document.type,
                    date: data.document.date
                };
                
                await loadDocumentStats();
                await loadMyDocuments();
                
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.dataset.fileId = fileObj.id;
                fileItem.innerHTML = `
                    <div class="file-icon">📄</div>
                    <div class="file-info">
                        <div class="file-name">${fileObj.name}</div>
                        <div class="file-meta">${fileObj.size} كيلوبايت • ${fileObj.type} • ${fileObj.date}</div>
                    </div>
                    <button class="remove-file" onclick="removeFile(${fileObj.id})">×</button>
                `;
                
                fileList.appendChild(fileItem);
                uploadedFilesDiv.style.display = 'block';
                
                // Update stats
                await loadDocumentStats();
            } else {
                alert(data.message || 'فشل رفع الملف');
            }
        } catch (error) {
            console.error('Error uploading file:', error);
            alert('حدث خطأ أثناء رفع الملف');
        }
    }
}

function removeFile(fileId) {
    uploadedFiles = uploadedFiles.filter(f => f.id !== fileId);
    const fileItem = document.querySelector(`[data-file-id="${fileId}"]`);
    if (fileItem) {
        fileItem.remove();
    }
    
    if (uploadedFiles.length === 0) {
        document.getElementById('uploadedFiles').style.display = 'none';
    }
}

function clearFiles() {
    uploadedFiles = [];
    const fileList = document.getElementById('fileList');
    if (fileList) {
        fileList.innerHTML = '';
    }
    document.getElementById('uploadedFiles').style.display = 'none';
}

// Load patient data
async function loadPatientData() {
    await loadDocumentStats();
    await loadMyDocuments();
}

async function loadDocumentStats() {
    try {
        const response = await fetch(`${API_BASE}/document-stats`, { credentials: 'include' });
        const data = await response.json();
        
        if (data.success) {
            const stats = data.stats;
            document.getElementById('totalCount').textContent = stats.total || 0;
            document.getElementById('labCount').textContent = stats.lab_results || 0;
            document.getElementById('imagingCount').textContent = stats.imaging || 0;
            document.getElementById('prescriptionCount').textContent = stats.prescriptions || 0;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadMyDocuments() {
    try {
        const response = await fetch(`${API_BASE}/my-documents`, { credentials: 'include' });
        const data = await response.json();
        
        if (data.success && data.documents.length > 0) {
            displayDocuments(data.documents);
        }
    } catch (error) {
        console.error('Error loading documents:', error);
    }
}
function displayDocuments(documents) {
    const fileList = document.getElementById('fileList');
    const uploadedFilesDiv = document.getElementById('uploadedFiles');
    const fileCountEl = document.getElementById('fileCount');
    
    if (!fileList || !uploadedFilesDiv) return;
    
    // مسح القائمة الحالية
    fileList.innerHTML = '';
    
    // إضافة المستندات
    documents.forEach(doc => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.dataset.fileId = doc.id;
        
        // أيقونة حسب نوع الملف
        let icon = '📄';
        if (doc.document_type.includes('أشعة')) {
            icon = '🩻';
        } else if (doc.document_type.includes('تحاليل')) {
            icon = '🧪';
        } else if (doc.document_type.includes('وصفة')) {
            icon = '💊';
        } else if (doc.document_type.includes('تقرير')) {
            icon = '📋';
        }
        
        fileItem.innerHTML = `
    <div class="file-icon">${icon}</div>
    <div class="file-info">
        <div class="file-name">${doc.file_name}</div>
        <div class="file-meta">${doc.document_type} • ${doc.upload_date}</div>
    </div>
    <button class="view-files-btn" onclick="viewDocument(${doc.id})" title="عرض الملف" style="padding: 8px 16px; font-size: 14px; margin-left: 8px;">
        👁️ عرض
    </button>
    <button class="remove-file" onclick="deleteDocument(${doc.id})" title="حذف الملف">×</button>
`;
        
        fileList.appendChild(fileItem);
    });
    
    // إظهار القسم
    uploadedFilesDiv.style.display = 'block';
    
    // تحديث العدد
    if (fileCountEl) {
        fileCountEl.textContent = documents.length;
    }
}

async function deleteDocument(documentId) {
    if (!confirm('هل أنت متأكد من حذف هذا المستند؟')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/delete-document/${documentId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('تم حذف المستند بنجاح');
            await loadDocumentStats();
            await loadMyDocuments();
        } else {
            alert(data.message || 'فشل حذف المستند');
        }
    } catch (error) {
        console.error('Error deleting document:', error);
        alert('حدث خطأ أثناء حذف المستند');
    }
}

// Load doctor data
async function loadDoctorData() {
    await loadDoctorStats();
    await loadPatients();
}

async function loadDoctorStats() {
    try {
        const response = await fetch(`${API_BASE}/doctor-stats`, { credentials: 'include' });
        const data = await response.json();
        
        if (data.success) {
            const stats = data.stats;
            
            // Update stats in the UI
            const statValues = document.querySelectorAll('.stat-value');
            if (statValues.length >= 3) {
                statValues[0].textContent = stats.patient_count || 0;
                statValues[1].textContent = stats.total_documents || 0;
                statValues[2].textContent = `اليوم: ${stats.today_documents || 0}`;
            }
        }
    } catch (error) {
        console.error('Error loading doctor stats:', error);
    }
}

async function loadPatients() {
    try {
        const response = await fetch(`${API_BASE}/patients`, { credentials: 'include' });
        const data = await response.json();
        
        if (data.success && data.patients.length > 0) {
            const patientsContainer = document.querySelector('.patients-card');
            
            // Clear existing patients (except search box and title)
            const patientItems = patientsContainer.querySelectorAll('.patient-item');
            patientItems.forEach(item => item.remove());
            
            // Add real patients
            data.patients.forEach(patient => {
                const patientItem = document.createElement('div');
                patientItem.className = 'patient-item';
                patientItem.innerHTML = `
                    <div class="patient-info">
                        <h3>${patient.name}</h3>
                        <div class="patient-details">العمر: ${patient.age || 'غير محدد'} • آخر زيارة: ${patient.last_visit || 'لا توجد'} • ${patient.document_count} ملف</div>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button class="view-files-btn" style="background: #059669;" onclick="addNoteToPatient(${patient.id})">
                            📝 ملاحظة
                        </button>
                        <button class="view-files-btn" onclick="viewPatientFiles(${patient.id})">
                            👁️ عرض الملفات
                        </button>
                    </div>
                `;
                patientsContainer.appendChild(patientItem);
            });
        }
    } catch (error) {
        console.error('Error loading patients:', error);
    }
}

async function viewPatientFiles(patientId) {
    try {
        const response = await fetch(`${API_BASE}/patient-documents/${patientId}`, { credentials: 'include' });
        const data = await response.json();
        
        if (data.success) {
            // إنشاء modal لعرض المستندات
            const modalHTML = `
                <div class="modal-overlay" onclick="closeModal()">
                    <div class="modal-content" onclick="event.stopPropagation()">
                        <div class="modal-header">
                            <h3>مستندات المريض</h3>
                            <button class="close-btn" onclick="closeModal()">×</button>
                        </div>
                        <div class="modal-body">
                            ${data.documents.length === 0 ? 
                                '<p style="text-align: center; padding: 20px; color: var(--text-secondary-light);">لا توجد مستندات</p>' :
                                data.documents.map(doc => {
                                    let icon = '📄';
                                    if (doc.document_type.includes('أشعة')) icon = '🩻';
                                    else if (doc.document_type.includes('تحاليل')) icon = '🧪';
                                    else if (doc.document_type.includes('وصفة')) icon = '💊';
                                    else if (doc.document_type.includes('تقرير')) icon = '📋';
                                    
                                    return `
    <div class="file-item">
        <div class="file-icon">${icon}</div>
        <div class="file-info">
            <div class="file-name">${doc.file_name}</div>
            <div class="file-meta">${doc.document_type} • ${doc.upload_date}</div>
        </div>
        <button class="view-files-btn" onclick="viewDocument(${doc.id}); closeModal();" style="padding: 8px 16px; font-size: 14px;">
            👁️ عرض
        </button>
    </div>
`;
                                    
                                }).join('')
                            }
                        </div>
                    </div>
                </div>
            `;
            
            // إضافة الـ modal للصفحة
            const modalDiv = document.createElement('div');
            modalDiv.innerHTML = modalHTML;
            document.body.appendChild(modalDiv.firstElementChild);
            
            // إضافة styles للـ modal
            addModalStyles();
        } else {
            alert(data.message || 'فشل تحميل المستندات');
        }
    } catch (error) {
        console.error('Error viewing patient files:', error);
        alert('حدث خطأ أثناء تحميل المستندات');
    }
}

function closeModal() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) {
        modal.remove();
    }
}

function addModalStyles() {
    if (document.getElementById('modal-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'modal-styles';
    style.textContent = `
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            padding: 20px;
        }
        
        .modal-content {
            background: var(--card-bg-light);
            border-radius: 12px;
            max-width: 700px;
            width: 100%;
            max-height: 80vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        }
        
        body.dark-mode .modal-content {
            background: var(--card-bg-dark);
        }
        
        .modal-header {
            padding: 24px;
            border-bottom: 1px solid var(--border-light);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        body.dark-mode .modal-header {
            border-bottom-color: var(--border-dark);
        }
        
        .modal-header h3 {
            margin: 0;
            font-size: 20px;
            font-weight: 600;
        }
        
        .modal-body {
            padding: 24px;
            overflow-y: auto;
        }
        
        .modal-body .file-item {
            margin-bottom: 12px;
        }
    `;
    document.head.appendChild(style);
}

// Search patients
const searchBox = document.querySelector('.search-box');
if (searchBox) {
    searchBox.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const patientItems = document.querySelectorAll('.patient-item');
        
        patientItems.forEach(item => {
            const patientName = item.querySelector('h3').textContent.toLowerCase();
            if (patientName.includes(searchTerm)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    });
}

// إضافة ملاحظة من الدكتور
async function addNoteToPatient(patientId) {
    const noteText = prompt('اكتب ملاحظة للمريض:');
    
    if (!noteText || noteText.trim() === '') {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/add-note`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
                patient_id: patientId,
                note_text: noteText
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ تم إضافة الملاحظة بنجاح');
        } else {
            alert(data.message || 'فشل إضافة الملاحظة');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('حدث خطأ أثناء إضافة الملاحظة');
    }
}

// عرض الإشعارات للمريض
async function showNotifications() {
    try {
        const response = await fetch(`${API_BASE}/my-notes`, { credentials: 'include' });
        const data = await response.json();
        
        if (data.success) {
            if (data.notes.length === 0) {
                alert('لا توجد إشعارات');
                return;
            }
            
            // إنشاء modal للإشعارات
            const notesHTML = data.notes.map(note => `
                <div style="padding: 15px; border-bottom: 1px solid #e5e7eb; ${!note.is_read ? 'background: #eff6ff;' : ''}">
                    <div style="font-weight: 600; margin-bottom: 5px;">د. ${note.doctor_name}</div>
                    <div style="color: #4b5563; margin-bottom: 5px;">${note.note_text}</div>
                    <div style="font-size: 12px; color: #9ca3af;">${note.created_at}</div>
                </div>
            `).join('');
            
            const modalHTML = `
                <div class="modal-overlay" onclick="closeModal()">
                    <div class="modal-content" onclick="event.stopPropagation()">
                        <div class="modal-header">
                            <h3>الإشعارات والملاحظات</h3>
                            <button class="close-btn" onclick="closeModal()">×</button>
                        </div>
                        <div class="modal-body">
                            ${notesHTML}
                        </div>
                    </div>
                </div>
            `;
            
            const modalDiv = document.createElement('div');
            modalDiv.innerHTML = modalHTML;
            document.body.appendChild(modalDiv.firstElementChild);
            
            addModalStyles();
            
            // تعليم كل الملاحظات كمقروءة
            data.notes.forEach(note => {
                if (!note.is_read) {
                    markNoteAsRead(note.id);
                }
            });
            
            // تحديث العداد
            updateNotificationCount();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('حدث خطأ أثناء تحميل الإشعارات');
    }
}

// تعليم الملاحظة كمقروءة
async function markNoteAsRead(noteId) {
    try {
        await fetch(`${API_BASE}/mark-note-read/${noteId}`, {
            method: 'POST',
            credentials: 'include'
        });
    } catch (error) {
        console.error('Error marking note as read:', error);
    }
}

// تحديث عدد الإشعارات
async function updateNotificationCount() {
    try {
        const response = await fetch(`${API_BASE}/unread-notes-count`, { credentials: 'include' });
        const data = await response.json();
        
        if (data.success) {
            const badge = document.getElementById('notificationBadge');
            if (badge) {
                if (data.count > 0) {
                    badge.textContent = data.count;
                    badge.style.display = 'flex';
                } else {
                    badge.style.display = 'none';
                }
            }
        }
    } catch (error) {
        console.error('Error updating notification count:', error);
    }
}

// متغير لنوع الحساب في التسجيل
let registerRole = 'patient';

// إظهار نموذج التسجيل
function showRegisterForm() {
    document.querySelector('.login-box:not(#registerBox)').style.display = 'none';
    document.getElementById('registerBox').style.display = 'block';
}

// إظهار نموذج تسجيل الدخول
function showLoginForm() {
    document.querySelector('.login-box:not(#registerBox)').style.display = 'block';
    document.getElementById('registerBox').style.display = 'none';
}

// اختيار نوع الحساب في التسجيل
function selectRegisterRole(role) {
    registerRole = role;
    const buttons = document.querySelectorAll('#registerBox .role-btn');
    buttons.forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`#registerBox [data-role="${role}"]`).classList.add('active');
}

// التسجيل
async function handleRegister() {
    const name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const age = document.getElementById('regAge').value;
    const phone = document.getElementById('regPhone').value;

    if (!name || !email || !password) {
        alert('يرجى ملء جميع الحقول المطلوبة');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                name: name,
                email: email,
                password: password,
                role: registerRole,
                age: age || null,
                phone: phone || null
            })
        });

        const data = await response.json();

        if (data.success) {
            alert('✅ تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول');
            showLoginForm();
            // مسح الحقول
            document.getElementById('regName').value = '';
            document.getElementById('regEmail').value = '';
            document.getElementById('regPassword').value = '';
            document.getElementById('regAge').value = '';
            document.getElementById('regPhone').value = '';
        } else {
            alert(data.message || 'فشل إنشاء الحساب');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('حدث خطأ أثناء إنشاء الحساب');
    }
}

// إعطاء صلاحية لدكتور
async function grantDoctorAccess() {
    const doctorEmail = document.getElementById('doctorEmail').value;
    
    if (!doctorEmail || doctorEmail.trim() === '') {
        alert('يرجى إدخال البريد الإلكتروني للطبيب');
        return;
    }
    
    // التحقق من صحة البريد الإلكتروني
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(doctorEmail)) {
        alert('يرجى إدخال بريد إلكتروني صحيح');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/grant-access`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                doctor_email: doctorEmail
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ تم منح الصلاحية للطبيب بنجاح!');
            document.getElementById('doctorEmail').value = ''; // مسح الحقل
        } else {
            alert(data.message || 'فشل منح الصلاحية');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('حدث خطأ أثناء منح الصلاحية');
    }
}
// عرض ملف
function viewDocument(documentId) {
    // فتح الملف في tab جديد
    window.open(`${API_BASE.replace('/api', '')}/view-document/${documentId}`, '_blank');
}

// تحديث loadPatientData لتحميل الإشعارات
const originalLoadPatientData = loadPatientData;
loadPatientData = async function() {
    await originalLoadPatientData();
    await updateNotificationCount();
};
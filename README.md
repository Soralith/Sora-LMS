# 🎓 Sora LMS
**Learning Management System berbasis Django + MySQL**

---

## 📋 Fitur Utama

- **👤 Autentikasi & Role** — Login (username/email), Register, 3 role: Admin, Guru, Siswa
- **📚 Manajemen Kelas** — Buat kelas, modul bertingkat, upload materi (file/video/teks/link)
- **📝 Tugas & Penilaian** — Buat tugas, upload jawaban, nilai + feedback dari guru
- **🧠 Kuis/Ujian Online** — Pilihan ganda, benar/salah, esai, timer, batas percobaan
- **📊 Progress Tracking** — Tracking per materi, laporan progres siswa per kelas
- **📢 Pengumuman** — Guru bisa buat pengumuman di tiap kelas
- **🔐 Kode Pendaftaran** — Kelas bisa dikunci dengan enrollment key
- **⚙️ Panel Admin** — Kelola semua user, kelas, dan data via dashboard admin
- **🤖 AI Chat** — Gemini API-powered asisten belajar

---

## ⚙️ Persyaratan Sistem

- Python 3.10+
- MySQL 8.0+ (via XAMPP/phpMyAdmin)
- pip

---

## 🚀 Cara Setup

### Langkah 1 — Buat Database di phpMyAdmin

1. Buka `http://127.0.0.1/phpmyadmin`
2. Klik **New** → beri nama: `sora_lms`
3. Collation: `utf8mb4_unicode_ci` → klik **Create**

### Langkah 2 — Konfigurasi Environment

Buat file `.env` di root folder:

```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
```

### Langkah 3 — Install & Migrasi

```bash
# Install semua dependencies
pip install -r requirements.txt

# Buat tabel database
python manage.py makemigrations
python manage.py migrate

# Buat akun admin
python manage.py createsuperuser
# atau gunakan:
python setup.py
```

### Langkah 4 — Jalankan Server

```bash
python manage.py runserver
```

Buka browser: **http://127.0.0.1:8000**

---

## 🗂️ Struktur Project

```
sora_lms/
├── manage.py
├── requirements.txt
├── setup.py
├── .env.example
├── sora_lms/              # Konfigurasi Django utama
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/          # User, Login, Register
│   ├── courses/           # Kelas, Modul, Materi
│   ├── assignments/      # Tugas & Penilaian
│   ├── quizzes/          # Kuis & Ujian
│   ├── dashboard/        # Dashboard & Progress
│   ├── ai_chat/          # AI Chat Gemini
│   └── komunitas         # Komunitas Chat
├── templates/             # HTML Templates
├── static/                # CSS, JS, Gambar
└── media/                 # File upload
```

---

## 📦 Dependencies

```
Django==4.2.11
mysqlclient==2.2.4
Pillow==10.2.0
python-dotenv
```

---

**Sora LMS** © 2024 — Dibuat dengan ❤️ menggunakan Django
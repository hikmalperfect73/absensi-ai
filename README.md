# 🎓 AbsensiAI — Deploy ke Railway

## 📁 Struktur
```
absensi-railway/
├── app.py
├── index.html
├── requirements.txt
├── Procfile
├── railway.json
├── init_db.py
├── api/
│   ├── students.py
│   └── attendance.py
└── config/
    └── database.py
```

---

## 🚀 Cara Deploy ke Railway

### 1. Upload ke GitHub
- Buat repo baru di GitHub
- Upload semua file ini ke repo tersebut

### 2. Buat project di Railway
- Buka https://railway.app
- Login dengan GitHub
- Klik **New Project → Deploy from GitHub repo**
- Pilih repo kamu

### 3. Tambah MySQL
- Di dashboard Railway, klik **+ New**
- Pilih **Database → MySQL**
- Railway otomatis connect ke app kamu

### 4. Buat tabel (sekali saja)
- Di Railway, buka tab **Settings → Variables**
- Klik **Shell** atau gunakan Railway CLI:
```
railway run python init_db.py
```

### 5. Selesai!
Railway kasih URL publik seperti:
```
https://absensi-ai.up.railway.app
```

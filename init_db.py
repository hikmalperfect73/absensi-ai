# init_db.py — jalankan SEKALI untuk buat tabel di Railway
# python init_db.py

from config.database import get_db

db = get_db()
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS students (
  id          VARCHAR(36) PRIMARY KEY,
  nama        VARCHAR(100) NOT NULL,
  nim         VARCHAR(30)  NOT NULL UNIQUE,
  kelas       VARCHAR(50)  NOT NULL,
  prodi       VARCHAR(100) NOT NULL,
  photo       LONGTEXT,
  descriptors LONGTEXT     NOT NULL,
  created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS attendance (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  student_id  VARCHAR(36)  NOT NULL,
  nama        VARCHAR(100) NOT NULL,
  nim         VARCHAR(30)  NOT NULL,
  kelas       VARCHAR(50)  NOT NULL,
  prodi       VARCHAR(100) NOT NULL,
  time        DATETIME     NOT NULL,
  date        DATE         NOT NULL,
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  INDEX idx_date (date),
  INDEX idx_student (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

db.commit()
cur.close()
db.close()
print("✅ Tabel berhasil dibuat!")

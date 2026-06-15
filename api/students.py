# api/students.py
from flask import Blueprint, request, jsonify
from config.database import get_db
import uuid
import json

students_bp = Blueprint('students', __name__)

# ── GET semua / satu mahasiswa ──
@students_bp.route('', methods=['GET'])
def get_students():
    student_id = request.args.get('id')
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        if student_id:
            cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
            row = cur.fetchone()
            if not row:
                return jsonify({'success': False, 'message': 'Mahasiswa tidak ditemukan'}), 404
            row['descriptors'] = json.loads(row['descriptors'])
            return jsonify({'success': True, 'data': row})
        else:
            cur.execute("SELECT * FROM students ORDER BY nama ASC")
            rows = cur.fetchall()
            for r in rows:
                r['descriptors'] = json.loads(r['descriptors'])
            return jsonify({'success': True, 'data': rows})
    finally:
        cur.close(); db.close()

# ── POST tambah mahasiswa ──
@students_bp.route('', methods=['POST'])
def add_student():
    body        = request.get_json() or {}
    nama        = (body.get('nama') or '').strip()
    nim         = (body.get('nim') or '').strip()
    kelas       = (body.get('kelas') or '').strip()
    prodi       = (body.get('prodi') or '').strip()
    photo       = body.get('photo')
    descriptors = body.get('descriptors', [])

    if not all([nama, nim, kelas, prodi]):
        return jsonify({'success': False, 'message': 'Nama, NIM, Kelas, dan Prodi wajib diisi'}), 400
    if not descriptors:
        return jsonify({'success': False, 'message': 'Data wajah tidak boleh kosong'}), 400

    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        # Cek NIM duplikat
        cur.execute("SELECT id FROM students WHERE nim = %s", (nim,))
        if cur.fetchone():
            return jsonify({'success': False, 'message': f'NIM {nim} sudah terdaftar'}), 409

        new_id    = str(uuid.uuid4())
        desc_json = json.dumps(descriptors)
        cur.execute(
            "INSERT INTO students (id, nama, nim, kelas, prodi, photo, descriptors) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (new_id, nama, nim, kelas, prodi, photo, desc_json)
        )
        db.commit()
        return jsonify({'success': True, 'message': f'{nama} berhasil didaftarkan',
                        'data': {'id': new_id, 'nama': nama, 'nim': nim, 'kelas': kelas, 'prodi': prodi}}), 201
    finally:
        cur.close(); db.close()

# ── DELETE satu atau semua ──
@students_bp.route('', methods=['DELETE'])
def delete_students():
    student_id = request.args.get('id')
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        if student_id:
            cur.execute("SELECT nama FROM students WHERE id = %s", (student_id,))
            row = cur.fetchone()
            if not row:
                return jsonify({'success': False, 'message': 'Mahasiswa tidak ditemukan'}), 404
            cur.execute("DELETE FROM students WHERE id = %s", (student_id,))
            db.commit()
            return jsonify({'success': True, 'message': f"{row['nama']} berhasil dihapus"})
        else:
            cur.execute("SELECT COUNT(*) as c FROM students")
            count = cur.fetchone()['c']
            cur.execute("DELETE FROM students")
            db.commit()
            return jsonify({'success': True, 'message': f'{count} mahasiswa berhasil dihapus'})
    finally:
        cur.close(); db.close()

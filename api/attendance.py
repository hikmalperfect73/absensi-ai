# api/attendance.py
from flask import Blueprint, request, jsonify
from config.database import get_db
from datetime import date, datetime
import json

attendance_bp = Blueprint('attendance', __name__)

# ── GET kehadiran ──
@attendance_bp.route('', methods=['GET'])
def get_attendance():
    action      = request.args.get('action')
    filter_date = request.args.get('date')
    db  = get_db()
    cur = db.cursor(dictionary=True)
    try:
        if action == 'stats':
            target = filter_date or str(date.today())
            cur.execute("SELECT COUNT(*) as c FROM students")
            total = cur.fetchone()['c']
            cur.execute("SELECT COUNT(*) as c FROM attendance WHERE date = %s", (target,))
            hadir = cur.fetchone()['c']
            return jsonify({'success': True, 'data': {
                'date': target,
                'total_students': total,
                'hadir': hadir,
                'belum_hadir': max(0, total - hadir),
                'persentase': round((hadir / total) * 100) if total > 0 else 0
            }})

        elif action == 'today' or not filter_date:
            today = str(date.today())
            cur.execute("SELECT * FROM attendance WHERE date = %s ORDER BY time DESC", (today,))
            rows = cur.fetchall()
            # Convert datetime to string
            for r in rows:
                r['time'] = str(r['time'])
                r['date'] = str(r['date'])
            return jsonify({'success': True, 'data': rows, 'total': len(rows), 'date': today})

        else:
            cur.execute("SELECT * FROM attendance WHERE date = %s ORDER BY time DESC", (filter_date,))
            rows = cur.fetchall()
            for r in rows:
                r['time'] = str(r['time'])
                r['date'] = str(r['date'])
            return jsonify({'success': True, 'data': rows, 'total': len(rows)})
    finally:
        cur.close(); db.close()

# ── POST catat kehadiran ──
@attendance_bp.route('', methods=['POST'])
def record_attendance():
    body       = request.get_json() or {}
    student_id = body.get('student_id', '')

    if not student_id:
        return jsonify({'success': False, 'message': 'student_id wajib diisi'}), 400

    db  = get_db()
    cur = db.cursor(dictionary=True)
    try:
        # Ambil data mahasiswa
        cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cur.fetchone()
        if not student:
            return jsonify({'success': False, 'message': 'Mahasiswa tidak ditemukan'}), 404

        # Cek sudah absen hari ini
        today = str(date.today())
        cur.execute("SELECT id FROM attendance WHERE student_id = %s AND date = %s", (student_id, today))
        if cur.fetchone():
            return jsonify({'success': False,
                            'message': f"{student['nama']} sudah tercatat hadir hari ini",
                            'already_recorded': True}), 409

        now   = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        nama  = body.get('nama',  student['nama'])
        nim   = body.get('nim',   student['nim'])
        kelas = body.get('kelas', student['kelas'])
        prodi = body.get('prodi', student['prodi'])

        cur.execute(
            "INSERT INTO attendance (student_id, nama, nim, kelas, prodi, time, date) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (student_id, nama, nim, kelas, prodi, now, today)
        )
        db.commit()
        return jsonify({'success': True, 'message': f'Kehadiran {nama} berhasil dicatat',
                        'data': {'student_id': student_id, 'nama': nama, 'nim': nim,
                                 'kelas': kelas, 'prodi': prodi, 'time': now, 'date': today}}), 201
    finally:
        cur.close(); db.close()

# ── DELETE reset hari ini / satu record ──
@attendance_bp.route('', methods=['DELETE'])
def delete_attendance():
    record_id = request.args.get('id')
    db  = get_db()
    cur = db.cursor()
    try:
        if record_id:
            cur.execute("DELETE FROM attendance WHERE id = %s", (record_id,))
            db.commit()
            if cur.rowcount == 0:
                return jsonify({'success': False, 'message': 'Record tidak ditemukan'}), 404
            return jsonify({'success': True, 'message': 'Record berhasil dihapus'})
        else:
            today = str(date.today())
            cur.execute("DELETE FROM attendance WHERE date = %s", (today,))
            db.commit()
            return jsonify({'success': True, 'message': f'{cur.rowcount} record kehadiran hari ini dihapus'})
    finally:
        cur.close(); db.close()

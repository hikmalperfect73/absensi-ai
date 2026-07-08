# api/export.py
import csv
import io
from datetime import date, datetime
from flask import Blueprint, request, Response
from config.database import get_db

export_bp = Blueprint('export', __name__)


def _to_csv_response(rows, fieldnames, filename):
    """
    Bangun response CSV yang aman untuk Excel:
    - utf-8-sig (BOM) supaya karakter non-ASCII tidak rusak di Excel
    - delimiter ';' karena Excel versi region Indonesia default-nya pakai ';'
    - csv.writer otomatis handle quoting kalau ada koma/newline di dalam field
    - QUOTE_MINIMAL + escapechar aman untuk field bertipe string apapun
    """
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=fieldnames,
        delimiter=';',
        quoting=csv.QUOTE_MINIMAL,
        extrasaction='ignore'  # kalau ada key ekstra di row, diabaikan bukan error
    )
    writer.writeheader()

    for row in rows:
        clean_row = {}
        for key in fieldnames:
            value = row.get(key)

            # Normalisasi datetime/date supaya format konsisten, bukan str() mentah
            if isinstance(value, datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(value, date):
                value = value.strftime('%Y-%m-%d')
            elif value is None:
                value = ''
            else:
                # Buang newline liar di dalam field (misal keterangan multi-baris)
                value = str(value).replace('\r\n', ' ').replace('\n', ' ')

            clean_row[key] = value
        writer.writerow(clean_row)

    csv_data = buffer.getvalue()
    buffer.close()

    # utf-8-sig -> tambahkan BOM di depan supaya Excel baca UTF-8 dengan benar
    output = csv_data.encode('utf-8-sig')

    return Response(
        output,
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': 'text/csv; charset=utf-8-sig'
        }
    )


# ── GET export attendance ke CSV ──
# Contoh: /api/export/attendance?date=2026-07-08
#         /api/export/attendance  (default: hari ini)
#         /api/export/attendance?date=all  (semua data)
@export_bp.route('/attendance', methods=['GET'])
def export_attendance():
    filter_date = request.args.get('date')

    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        if filter_date == 'all':
            cur.execute("SELECT * FROM attendance ORDER BY date DESC, time DESC")
            fname_suffix = 'semua'
        else:
            target = filter_date or str(date.today())
            cur.execute(
                "SELECT * FROM attendance WHERE date = %s ORDER BY time DESC",
                (target,)
            )
            fname_suffix = target

        rows = cur.fetchall()

        fieldnames = ['nim', 'nama', 'kelas', 'prodi', 'date', 'time']
        filename = f'absensi_{fname_suffix}.csv'

        return _to_csv_response(rows, fieldnames, filename)
    finally:
        cur.close(); db.close()


# ── GET export students ke CSV ──
# Contoh: /api/export/students
@export_bp.route('/students', methods=['GET'])
def export_students():
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute("SELECT id, nama, nim, kelas, prodi FROM students ORDER BY nama ASC")
        rows = cur.fetchall()

        fieldnames = ['nim', 'nama', 'kelas', 'prodi']
        filename = 'data_mahasiswa.csv'

        return _to_csv_response(rows, fieldnames, filename)
    finally:
        cur.close(); db.close()

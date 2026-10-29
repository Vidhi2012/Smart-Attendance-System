"""Storage layer: students, attendance, users and messages (JSON + CSV backup)."""
import csv
import hashlib
import hmac
import json
import os
import re
import secrets
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PHOTO_DIR = os.path.join(DATA_DIR, "student_images")
FACE_DIR = os.path.join(DATA_DIR, "faces")

STUDENT_JSON = os.path.join(DATA_DIR, "students.json")
STUDENT_CSV = os.path.join(DATA_DIR, "students.csv")
ATTENDANCE_JSON = os.path.join(DATA_DIR, "attendance.json")
USER_JSON = os.path.join(DATA_DIR, "users.json")
MESSAGE_JSON = os.path.join(DATA_DIR, "messages.json")
SETTINGS_JSON = os.path.join(DATA_DIR, "settings.json")

CSV_HEADERS = ["student_id", "prn", "name", "department", "class", "division",
               "email", "mobile", "photo", "registered_date"]
ATTENDANCE_FIELDS = ["student_id", "prn", "name", "date", "time", "status",
                     "recognition"]

DEPARTMENTS = ["Computer Science", "Information Technology", "Electronics",
               "Mechanical", "Civil"]
ROLES = ["Faculty", "Admin"]          # staff who operate the system

for _folder in (DATA_DIR, PHOTO_DIR, FACE_DIR):
    os.makedirs(_folder, exist_ok=True)


# ---------------------------------------------------------------- JSON utils
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


def save_json(path, data):
    """Atomic write so a crash never leaves a half-written file."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=4, ensure_ascii=False)
    os.replace(tmp, path)


# ---------------------------------------------------------------- validators
def valid_student_id(v): return bool(re.fullmatch(r"[A-Za-z0-9]{2,20}", v))
def valid_prn(v): return bool(re.fullmatch(r"[0-9]{8,20}", v))
def valid_name(v): return bool(re.fullmatch(r"[A-Za-z ]{2,50}", v))
def valid_department(v): return bool(re.fullmatch(r"[A-Za-z .&-]{2,60}", v))
def valid_mobile(v): return bool(re.fullmatch(r"[6-9][0-9]{9}", v))
def valid_email(v): return bool(re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", v))
def valid_user_id(v): return bool(re.fullmatch(r"[A-Za-z0-9_-]{3,20}", v))
def valid_full_name(v): return bool(re.fullmatch(r"[A-Za-z ]{2,60}", v))
def valid_password(v):
    return bool(re.fullmatch(r"(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}", v))


# ------------------------------------------------------------------ students
def list_students():
    return load_json(STUDENT_JSON)


def get_student(student_id):
    for s in list_students():
        if s.get("student_id") == student_id:
            return s
    return None


def search_students(query):
    q = query.strip().lower()
    if not q:
        return list_students()
    return [s for s in list_students()
            if q in str(s.get("student_id", "")).lower()
            or q in str(s.get("prn", "")).lower()
            or q in str(s.get("name", "")).lower()]


def photo_path(student):
    name = student.get("photo", "") if student else ""
    path = os.path.join(PHOTO_DIR, name) if name else ""
    return path if path and os.path.exists(path) else None


def _write_student_csv(students):
    with open(STUDENT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_HEADERS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(students)


def add_student(student):
    """Add a student. Raises ValueError on duplicate ID / PRN."""
    students = list_students()
    for s in students:
        if s["student_id"].lower() == student["student_id"].lower():
            raise ValueError("This Student ID is already registered.")
        if s["prn"] == student["prn"]:
            raise ValueError("This PRN is already registered.")
    student = dict(student)
    student["registered_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    students.append(student)
    save_json(STUDENT_JSON, students)
    _write_student_csv(students)
    return student


def delete_student(student_id):
    """Remove a student together with photo, face samples and attendance."""
    students = list_students()
    target = next((s for s in students if s["student_id"] == student_id), None)
    if target is None:
        return False
    students = [s for s in students if s["student_id"] != student_id]
    save_json(STUDENT_JSON, students)
    _write_student_csv(students)
    save_json(ATTENDANCE_JSON,
              [r for r in load_json(ATTENDANCE_JSON) if r.get("student_id") != student_id])
    path = photo_path(target)
    if path:
        os.remove(path)
    face_folder = os.path.join(FACE_DIR, student_id)
    if os.path.isdir(face_folder):
        for f in os.listdir(face_folder):
            os.remove(os.path.join(face_folder, f))
        os.rmdir(face_folder)
    return True


def safe_photo_name(student_id, name):
    safe = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_") or "student"
    return f"{student_id}_{safe}.jpg"


# ---------------------------------------------------------------- attendance
def list_attendance(student_id=None, date=None):
    records = load_json(ATTENDANCE_JSON)
    if student_id:
        records = [r for r in records if r.get("student_id") == student_id]
    if date:
        records = [r for r in records if r.get("date") == date]
    return sorted(records, key=lambda r: (r.get("date", ""), r.get("time", "")),
                  reverse=True)


def mark_attendance(student, recognition="Face Recognized"):
    """Mark a student present for today. Returns (created, record)."""
    records = load_json(ATTENDANCE_JSON)
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    for r in records:
        if r.get("student_id") == student["student_id"] and r.get("date") == today:
            return False, r
    record = {
        "student_id": student["student_id"], "prn": student.get("prn", ""),
        "name": student.get("name", ""), "date": today,
        "time": now.strftime("%H:%M:%S"), "status": "Present",
        "recognition": recognition,
    }
    records.append(record)
    save_json(ATTENDANCE_JSON, records)
    return True, record


def attendance_summary(student_id):
    """Class days = distinct dates on which anyone was marked present."""
    records = load_json(ATTENDANCE_JSON)
    class_days = {r["date"] for r in records if r.get("date")}
    present = {r["date"] for r in records
               if r.get("student_id") == student_id and r.get("date")}
    total = len(class_days)
    pct = round(len(present) / total * 100) if total else 0
    return {"total": total, "present": len(present),
            "absent": total - len(present), "percent": pct}


def today_stats():
    today = datetime.now().strftime("%Y-%m-%d")
    students = list_students()
    present_ids = {r["student_id"] for r in list_attendance(date=today)}
    present = len([s for s in students if s["student_id"] in present_ids])
    total = len(students)
    return {"students": total, "present": present, "absent": total - present,
            "rate": round(present / total * 100) if total else 0,
            "records": len(load_json(ATTENDANCE_JSON))}


def export_attendance_csv(path, records):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=ATTENDANCE_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


# --------------------------------------------------------------------- users
_ITERATIONS = 200_000


def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                 bytes.fromhex(salt), _ITERATIONS).hex()
    return f"pbkdf2${_ITERATIONS}${salt}${digest}"


def _verify(password, stored):
    if stored.startswith("pbkdf2$"):
        _, iters, salt, digest = stored.split("$")
        calc = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                   bytes.fromhex(salt), int(iters)).hex()
        return hmac.compare_digest(calc, digest)
    # legacy unsalted SHA-256 accounts from the first version
    legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy, stored)


def create_user(full_name, user_id, email, role, department, password):
    users = load_json(USER_JSON)
    for u in users:
        if u.get("email", "").lower() == email.lower():
            raise ValueError("This email is already registered.")
        if u.get("user_id", "").lower() == user_id.lower():
            raise ValueError("This Student/Staff ID already exists.")
    user = {"full_name": full_name, "user_id": user_id, "email": email,
            "role": role, "department": department,
            "password": hash_password(password)}
    users.append(user)
    save_json(USER_JSON, users)
    return user


def authenticate(email, password):
    users = load_json(USER_JSON)
    for u in users:
        if u.get("email", "").lower() == email.lower() and _verify(password, u.get("password", "")):
            if not u["password"].startswith("pbkdf2$"):  # upgrade old hash
                u["password"] = hash_password(password)
                save_json(USER_JSON, users)
            return u
    return None


# ------------------------------------------------------------------ messages
def save_message(email, message):
    msgs = load_json(MESSAGE_JSON)
    msgs.append({"email": email, "message": message,
                 "sent": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    save_json(MESSAGE_JSON, msgs)


# ------------------------------------------------------------------ settings
def get_setting(key, default=None):
    try:
        with open(SETTINGS_JSON, "r", encoding="utf-8") as fh:
            return json.load(fh).get(key, default)
    except (FileNotFoundError, json.JSONDecodeError, OSError, AttributeError):
        return default


def set_setting(key, value):
    try:
        with open(SETTINGS_JSON, "r", encoding="utf-8") as fh:
            settings = json.load(fh)
        if not isinstance(settings, dict):
            settings = {}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        settings = {}
    settings[key] = value
    tmp = SETTINGS_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=4)
    os.replace(tmp, SETTINGS_JSON)

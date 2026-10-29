# SmartMark — AI Smart Attendance System

Register students with a webcam face scan, then let the camera recognise them and
record attendance automatically. Built with Python, OpenCV and CustomTkinter.

## Run

```bash
pip install -r requirements.txt
python app.py
```

Needs Python 3.9+ and a webcam. Use `opencv-contrib-python` (not plain `opencv-python`) —
it provides the face recogniser. Without it the app still runs, with face *detection*
and manual check-in only.

## How the files connect

| File | Role |
| --- | --- |
| `app.py` | Entry point. Window, sidebar, page routing, login session |
| `home.py` | Landing page → Login / Register / Take attendance |
| `login.py` | Log in & sign up (salted PBKDF2 hashes) |
| `main.py` | Student registration + face capture, and the Students directory |
| `Attendance_dashboard.py` | Dashboard overview + live recognition, history, CSV export |
| `contact.py` | Support form (messages saved to `data/messages.json`) |
| `theme.py` | Colours, fonts, button styles |
| `widgets.py` | Shared UI parts (cards, fields, tables, camera view) |
| `data.py` | All reading/writing of students, attendance, users |
| `face_engine.py` | Face detection (Haar) + recognition (LBPH) |

Flow: **Home → Log in → Dashboard**. Register a student (details + 12 face samples) →
recogniser retrains → **Attendance → Start camera** → recognised students are marked present.

## Data (created automatically in `data/`)

`students.json` / `students.csv`, `attendance.json`, `users.json`, `messages.json`,
`student_images/`, `faces/<student_id>/`, `trainer.yml`.

## Tuning

`face_engine.THRESHOLD` (default 70) — lower is stricter. If real students show as
"Unknown", raise it a little; if the wrong person is matched, lower it.
Register in the same lighting you will use for attendance.

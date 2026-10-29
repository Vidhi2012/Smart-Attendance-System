"""Face detection + recognition (OpenCV Haar cascade + LBPH recogniser)."""
import json
import os
import cv2
import numpy as np
from data import DATA_DIR, FACE_DIR

MODEL_FILE = os.path.join(DATA_DIR, "trainer.yml")
LABEL_FILE = os.path.join(DATA_DIR, "labels.json")
FACE_SIZE = (200, 200)
# LBPH distance: lower = better match. Above this we call the face "Unknown".
THRESHOLD = 70.0

_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
_recognizer = None
_labels = {}


def recognition_available():
    """True when opencv-contrib-python (cv2.face) is installed."""
    return hasattr(cv2, "face")


def detect_faces(frame):
    gray = cv2.equalizeHist(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    faces = _cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5,
                                      minSize=(80, 80))
    return [tuple(int(v) for v in f) for f in faces]


def largest_face(faces):
    return max(faces, key=lambda f: f[2] * f[3]) if faces else None


def crop_face(frame, box):
    x, y, w, h = box
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face = cv2.resize(gray[y:y + h, x:x + w], FACE_SIZE)
    return cv2.equalizeHist(face)


def crop_portrait(frame, box, margin=0.35):
    """Colour crop (with margin) used as the student's profile photo."""
    x, y, w, h = box
    m = int(max(w, h) * margin)
    H, W = frame.shape[:2]
    portrait = frame[max(0, y - m):min(H, y + h + m), max(0, x - m):min(W, x + w + m)]
    return cv2.resize(portrait, (320, 320))


# -------------------------------------------------------------- persistence
def save_samples(student_id, samples):
    folder = os.path.join(FACE_DIR, student_id)
    os.makedirs(folder, exist_ok=True)
    for i, face in enumerate(samples):
        cv2.imwrite(os.path.join(folder, f"{i:03d}.jpg"), face)
    return len(samples)


def train():
    """(Re)train from every sample under data/faces. Returns number of students."""
    global _recognizer, _labels
    _recognizer, _labels = None, {}
    if not recognition_available():
        return 0
    images, labels, mapping = [], [], {}
    for sid in sorted(os.listdir(FACE_DIR)):
        folder = os.path.join(FACE_DIR, sid)
        if not os.path.isdir(folder):
            continue
        for name in os.listdir(folder):
            img = cv2.imread(os.path.join(folder, name), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            label = mapping.setdefault(sid, len(mapping))
            images.append(cv2.resize(img, FACE_SIZE))
            labels.append(label)
    if not images:
        for f in (MODEL_FILE, LABEL_FILE):
            if os.path.exists(f):
                os.remove(f)
        return 0
    recognizer = cv2.face.LBPHFaceRecognizer_create(radius=2, neighbors=8,
                                                    grid_x=8, grid_y=8)
    recognizer.train(images, np.array(labels))
    recognizer.write(MODEL_FILE)
    with open(LABEL_FILE, "w", encoding="utf-8") as fh:
        json.dump({str(v): k for k, v in mapping.items()}, fh)
    _recognizer, _labels = recognizer, {v: k for k, v in mapping.items()}
    return len(mapping)


def _load():
    global _recognizer, _labels
    if _recognizer is not None:
        return True
    if not (recognition_available() and os.path.exists(MODEL_FILE)
            and os.path.exists(LABEL_FILE)):
        return False
    try:
        rec = cv2.face.LBPHFaceRecognizer_create()
        rec.read(MODEL_FILE)
        with open(LABEL_FILE, "r", encoding="utf-8") as fh:
            _labels = {int(k): v for k, v in json.load(fh).items()}
        _recognizer = rec
        return True
    except Exception:
        return False


def model_ready():
    return _load()


def identify(frame, box):
    """Return (student_id | None, distance) for one detected face."""
    if not _load():
        return None, None
    label, distance = _recognizer.predict(crop_face(frame, box))
    sid = _labels.get(label)
    return (sid if distance <= THRESHOLD else None), float(distance)

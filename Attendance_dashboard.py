"""Dashboard overview and the live attendance screen."""
from datetime import datetime
from tkinter import filedialog
import cv2
import customtkinter as ctk
import data
import face_engine as fe
import theme as T
from widgets import (Page, Card, PageHeader, StatCard, DataTable, CameraView, avatar,
                     Label)

GREEN_BGR, AMBER_BGR = (94, 197, 34), (11, 158, 245)
STREAK_TO_MARK = 3          # consecutive recognitions needed before marking


# ================================================================== overview
class OverviewPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x", padx=32, pady=(28, 18))
        self.greeting = PageHeader(head, "Hello", "")
        self.greeting.pack(side="left")
        T.primary_button(head, "◉  Take attendance", lambda: app.show("attendance"),
                         width=190).pack(side="right")

        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", padx=32)
        stats.columnconfigure((0, 1, 2, 3), weight=1, uniform="o")
        self.s_students = StatCard(stats, "Registered students")
        self.s_present = StatCard(stats, "Present today", tint=T.SUCCESS)
        self.s_absent = StatCard(stats, "Not yet marked", tint=T.ACCENT)
        self.s_rate = StatCard(stats, "Today's attendance", tint="#F59E0B")
        for i, card in enumerate((self.s_students, self.s_present, self.s_absent, self.s_rate)):
            card.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 8, 0 if i == 3 else 8))

        lower = ctk.CTkFrame(self, fg_color="transparent")
        lower.pack(fill="both", expand=True, padx=32, pady=(18, 24))
        lower.columnconfigure(0, weight=6, uniform="l")
        lower.columnconfigure(1, weight=4, uniform="l")
        lower.rowconfigure(0, weight=1)

        recent = Card(lower)
        recent.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(recent, text="Today's check-ins", font=T.font(16, "bold"),
                     text_color=T.TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 10))
        self.table = DataTable(recent, [("time", "Time", 90), ("name", "Student", 200),
                                        ("id", "ID", 90), ("how", "Method", 140)], height=9)
        self.table.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        side = Card(lower)
        side.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(side, text="Quick actions", font=T.font(16, "bold"),
                     text_color=T.TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 12))
        T.primary_button(side, "＋  Register a student",
                         lambda: app.show("register")).pack(fill="x", padx=24, pady=4)
        T.ghost_button(side, "☷  View students",
                       lambda: app.show("students")).pack(fill="x", padx=24, pady=4)
        T.ghost_button(side, "✉  Contact support",
                       lambda: app.show("contact")).pack(fill="x", padx=24, pady=4)
        self.engine = Label(side, text="", font=T.font(12), justify="left",
                                   wraplength=300, text_color=T.TEXT_SECONDARY, anchor="w")
        self.engine.pack(anchor="w", padx=24, pady=(18, 0))

    def on_show(self, **kwargs):
        hour = datetime.now().hour
        part = "morning" if hour < 12 else "afternoon" if hour < 18 else "evening"
        first = (self.app.user or {}).get("full_name", "there").split()[0]
        for child in self.greeting.winfo_children():
            child.destroy()
        ctk.CTkLabel(self.greeting, text=f"Good {part}, {first}", font=T.font(26, "bold"),
                     text_color=T.TEXT_PRIMARY, anchor="w").pack(anchor="w")
        ctk.CTkLabel(self.greeting, text=datetime.now().strftime("%A, %d %B %Y"),
                     font=T.font(13), text_color=T.TEXT_SECONDARY, anchor="w").pack(anchor="w")
        st = data.today_stats()
        self.s_students.set(st["students"])
        self.s_present.set(st["present"])
        self.s_absent.set(st["absent"])
        self.s_rate.set(f'{st["rate"]}%')
        today = datetime.now().strftime("%Y-%m-%d")
        self.table.set_rows([(f'{r["student_id"]}', (r["time"], r["name"], r["student_id"],
                                                    r["recognition"]))
                             for r in data.list_attendance(date=today)])
        if not fe.recognition_available():
            msg = "Recogniser: install opencv-contrib-python to enable face recognition."
        elif not fe.model_ready():
            msg = "Recogniser: no faces trained yet. Register a student to begin."
        else:
            msg = "Recogniser: ready."
        self.engine.configure(text=msg)


# ================================================================ attendance
class AttendancePage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.selected = None
        self._frame_no, self._labels = 0, []
        self._streak, self._announced, self._names = {}, set(), {}

        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x", padx=32, pady=(28, 16))
        PageHeader(head, "Attendance",
                   "Start the camera to mark students automatically, or check one in manually."
                   ).pack(side="left")

        cols = ctk.CTkFrame(self, fg_color="transparent")
        cols.pack(fill="both", expand=True, padx=32, pady=(0, 24))
        cols.columnconfigure(0, weight=0)
        cols.columnconfigure(1, weight=1)
        cols.rowconfigure(0, weight=1)
        self._build_left(cols)
        self._build_right(cols)

    # ------------------------------------------------------------------ left
    def _build_left(self, parent):
        left = ctk.CTkFrame(parent, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        cam_card = Card(left)
        cam_card.pack(fill="x")
        body = ctk.CTkFrame(cam_card, fg_color="transparent")
        body.pack(padx=20, pady=20)
        top = ctk.CTkFrame(body, fg_color="transparent")
        top.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(top, text="Live recognition", font=T.font(16, "bold"),
                     text_color=T.TEXT_PRIMARY).pack(side="left")
        self.cam_btn = T.primary_button(top, "Start camera", self.toggle_camera,
                                        width=130, height=34)
        self.cam_btn.pack(side="right")
        self.camera = CameraView(body, width=400, height=300, on_frame=self._on_frame)
        self.camera.pack()
        self.status = Label(body, text="Camera is off", font=T.font(12),
                            text_color=T.TEXT_SECONDARY, wraplength=390,
                            justify="left", anchor="w")
        self.status.pack(anchor="w", pady=(10, 0))

        manual = Card(left)
        manual.pack(fill="x", pady=(12, 0))
        mb = ctk.CTkFrame(manual, fg_color="transparent")
        mb.pack(fill="x", padx=20, pady=18)
        ctk.CTkLabel(mb, text="Manual check-in", font=T.font(16, "bold"),
                     text_color=T.TEXT_PRIMARY).pack(anchor="w", pady=(0, 8))
        row = ctk.CTkFrame(mb, fg_color="transparent")
        row.pack(fill="x")
        self.search = ctk.CTkEntry(row, height=40, corner_radius=10, border_color=T.BORDER,
                                   fg_color=T.INPUT_BG, text_color=T.TEXT_PRIMARY,
                                   placeholder_text="Student ID / PRN / Name", font=T.font(13))
        self.search.pack(side="left", fill="x", expand=True)
        self.search.bind("<Return>", lambda e: self.search_student())
        T.primary_button(row, "Search", self.search_student, width=84,
                         height=40).pack(side="left", padx=(8, 0))
        T.ghost_button(mb, "Mark selected student present", self.mark_selected,
                       height=38).pack(fill="x", pady=(10, 0))

    # ----------------------------------------------------------------- right
    def _build_right(self, parent):
        right = ctk.CTkFrame(parent, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)

        self.profile = Card(right, height=110)
        self.profile.grid(row=0, column=0, sticky="ew")
        self.profile.pack_propagate(False)
        self._render_profile(None)

        stats = ctk.CTkFrame(right, fg_color="transparent")
        stats.grid(row=1, column=0, sticky="ew", pady=12)
        stats.columnconfigure((0, 1, 2, 3), weight=1, uniform="a")
        self.stat = {
            "total": StatCard(stats, "Class days"),
            "present": StatCard(stats, "Present", tint=T.SUCCESS),
            "absent": StatCard(stats, "Absent", tint=T.ACCENT),
            "percent": StatCard(stats, "Attendance", tint="#F59E0B"),
        }
        for i, key in enumerate(("total", "present", "absent", "percent")):
            self.stat[key].grid(row=0, column=i, sticky="ew",
                                padx=(0 if i == 0 else 6, 0 if i == 3 else 6))

        hist = Card(right)
        hist.grid(row=2, column=0, sticky="nsew")
        hh = ctk.CTkFrame(hist, fg_color="transparent")
        hh.pack(fill="x", padx=20, pady=(18, 8))
        ctk.CTkLabel(hh, text="Attendance history", font=T.font(16, "bold"),
                     text_color=T.TEXT_PRIMARY).pack(side="left")
        T.ghost_button(hh, "Export CSV", self.export, width=110, height=34).pack(side="right")
        self.table = DataTable(hist, [("date", "Date", 100), ("time", "Time", 90),
                                      ("name", "Student", 170), ("status", "Status", 90),
                                      ("how", "Recognition", 140)], height=7)
        self.table.pack(fill="both", expand=True, padx=20, pady=(0, 18))

    # ------------------------------------------------------- profile + history
    def _render_profile(self, student):
        for child in self.profile.winfo_children():
            child.destroy()
        if not student:
            ctk.CTkLabel(self.profile, text="No student selected — search, or start the "
                         "camera and let SmartMark find them.", font=T.font(13),
                         text_color=T.TEXT_SECONDARY).place(relx=0.5, rely=0.5, anchor="center")
            return
        row = ctk.CTkFrame(self.profile, fg_color="transparent")
        row.pack(fill="both", expand=True, padx=20, pady=14)
        avatar(row, student["name"], 76, data.photo_path(student)).pack(side="left")
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", padx=16)
        ctk.CTkLabel(info, text=student["name"], font=T.font(20, "bold"),
                     text_color=T.TEXT_PRIMARY, anchor="w").pack(anchor="w")
        ctk.CTkLabel(info, text=f'{student["student_id"]}  ·  PRN {student["prn"]}  ·  '
                     f'{student["department"]}  ·  {student["class"]}-{student["division"]}',
                     font=T.font(12), text_color=T.TEXT_SECONDARY, anchor="w").pack(anchor="w")

    def _select(self, student):
        self.selected = student
        self._render_profile(student)
        self._refresh_stats()

    def _refresh_stats(self):
        if not self.selected:
            for key in ("total", "present", "absent"):
                self.stat[key].set(0)
            self.stat["percent"].set("0%")
            self.table.set_rows([])
            return
        s = data.attendance_summary(self.selected["student_id"])
        self.stat["total"].set(s["total"])
        self.stat["present"].set(s["present"])
        self.stat["absent"].set(s["absent"])
        self.stat["percent"].set(f'{s["percent"]}%')
        rows = data.list_attendance(self.selected["student_id"])
        self.table.set_rows([(i, (r["date"], r["time"], r["name"], r["status"],
                                  r["recognition"])) for i, r in enumerate(rows)])

    # ----------------------------------------------------------------- search
    def search_student(self):
        query = self.search.get().strip()
        if not query:
            return self.app.toast.show("Enter a Student ID, PRN or name.", "warning")
        matches = data.search_students(query)
        if not matches:
            return self.app.toast.show("No student found.", "error")
        self._select(matches[0])
        if len(matches) > 1:
            self.app.toast.show(f"{len(matches)} matches — showing the first.", "info")

    def mark_selected(self):
        if not self.selected:
            return self.app.toast.show("Search and select a student first.", "warning")
        if self.camera.running and not self._labels:
            return self.app.toast.show("No face in view — position the student at the camera.",
                                       "warning")
        self._mark(self.selected, "Manual Entry")

    def _mark(self, student, recognition):
        created, _ = data.mark_attendance(student, recognition)
        self._select(student)
        if created:
            self.app.toast.show(f'✓ {student["name"]} marked present at '
                                f'{datetime.now():%H:%M:%S}.', "success")
        else:
            self.app.toast.show(f'{student["name"]} is already marked present today.', "info")
        return created

    # ----------------------------------------------------------------- camera
    def toggle_camera(self):
        if self.camera.running:
            self.camera.stop()
            self.cam_btn.configure(text="Start camera")
            self.status.configure(text="Camera is off", text_color=T.TEXT_SECONDARY)
            self._labels, self._streak = [], {}
            return
        self._names = {s["student_id"]: s["name"] for s in data.list_students()}
        self._announced, self._streak = set(), {}
        if not self.camera.start():
            return self.status.configure(text="Camera unavailable.", text_color=T.ERROR)
        self.cam_btn.configure(text="Stop camera")
        if not fe.recognition_available():
            msg = ("Face detection only. Install opencv-contrib-python for automatic "
                   "recognition; use manual check-in meanwhile.")
        elif not fe.model_ready():
            msg = "No registered faces yet — register a student first."
        else:
            msg = "Scanning… students are marked automatically when recognised."
        self.status.configure(text=msg, text_color=T.TEXT_SECONDARY)

    def _on_frame(self, frame):
        self._frame_no += 1
        if self._frame_no % 3 == 1:
            ready = fe.recognition_available() and fe.model_ready()
            labels = []
            for box in fe.detect_faces(frame):
                sid, dist = fe.identify(frame, box) if ready else (None, None)
                labels.append((box, sid, dist))
            self._labels = labels
            self._after_detection()
        for (x, y, w, h), sid, _ in self._labels:
            colour = GREEN_BGR if sid else AMBER_BGR
            cv2.rectangle(frame, (x, y), (x + w, y + h), colour, 3)
            text = self._names.get(sid, "Unknown") if sid else "Unknown"
            (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
            cv2.rectangle(frame, (x, y - th - 14), (x + tw + 12, y), colour, -1)
            cv2.putText(frame, text, (x + 6, y - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                        (255, 255, 255), 2)
        return frame

    def _after_detection(self):
        seen = {sid for _, sid, _ in self._labels if sid}
        self._streak = {sid: self._streak.get(sid, 0) + 1 for sid in seen}
        for sid, count in self._streak.items():
            if count >= STREAK_TO_MARK and sid not in self._announced:
                self._announced.add(sid)
                student = data.get_student(sid)
                if student:
                    self._mark(student, "Face Recognized")

    # ----------------------------------------------------------------- export
    def export(self):
        records = data.list_attendance(self.selected["student_id"] if self.selected else None)
        if not records:
            return self.app.toast.show("No attendance records to export.", "warning")
        path = filedialog.asksaveasfilename(title="Export attendance", defaultextension=".csv",
                                            filetypes=[("CSV files", "*.csv")],
                                            initialfile="attendance.csv")
        if not path:
            return
        try:
            data.export_attendance_csv(path, records)
            self.app.toast.show("Attendance exported.", "success")
        except OSError as error:
            self.app.toast.show(f"Export failed: {error}", "error", 5000)

    # -------------------------------------------------------------- lifecycle
    def on_show(self, **kwargs):
        sid = kwargs.get("student_id")
        if sid:
            student = data.get_student(sid)
            if student:
                self._select(student)
        else:
            self._refresh_stats()

    def on_hide(self):
        if self.camera.running:
            self.toggle_camera()

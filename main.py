"""Student registration (with face capture) and the registered-students directory."""
import os
import tkinter.messagebox as messagebox
import cv2
import customtkinter as ctk
from PIL import Image
import data
import face_engine as fe
import theme as T
from widgets import (Page, Card, PageHeader, Field, CameraView, DataTable, avatar,
                     pil_from_bgr, blank_image, Label, chip)

SAMPLES_NEEDED = 12


# =============================================================== registration
class RegistrationPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.samples, self.photo, self._capturing = [], None, False
        self._faces, self._frame_no = [], 0

        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x", padx=32, pady=(28, 16))
        PageHeader(head, "Register a student",
                   "Add the details, then capture a clear front-facing scan.").pack(side="left")
        self.count_chip = chip(head, "0 registered")
        self.count_chip.pack(side="right")

        cols = ctk.CTkFrame(self, fg_color="transparent")
        cols.pack(fill="both", expand=True, padx=32, pady=(0, 24))
        cols.columnconfigure(0, weight=5, uniform="r")
        cols.columnconfigure(1, weight=5, uniform="r")
        cols.rowconfigure(0, weight=1)
        self._build_form(cols)
        self._build_camera(cols)

    # ------------------------------------------------------------------ form
    def _build_form(self, parent):
        card = Card(parent)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=28, pady=24)
        form.columnconfigure((0, 1), weight=1, uniform="f")
        self.f_id = Field(form, "Student ID", "e.g. CS101")
        self.f_prn = Field(form, "PRN", "8-20 digits")
        self.f_name = Field(form, "Full name", "Aarav Sharma")
        self.f_dept = Field(form, "Department", "Select department", values=data.DEPARTMENTS)
        self.f_class = Field(form, "Class", "e.g. TY")
        self.f_div = Field(form, "Division", "e.g. A")
        self.f_email = Field(form, "Email", "student@college.edu")
        self.f_mobile = Field(form, "Mobile", "10-digit number")
        layout = [(self.f_id, 0, 0), (self.f_prn, 0, 1), (self.f_name, 1, None),
                  (self.f_dept, 2, None), (self.f_class, 3, 0), (self.f_div, 3, 1),
                  (self.f_email, 4, None), (self.f_mobile, 5, None)]
        for field, row, col in layout:
            if col is None:
                field.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 10))
            else:
                field.grid(row=row, column=col, sticky="ew", pady=(0, 10),
                           padx=(0, 6) if col == 0 else (6, 0))
        self.error = Label(form, text="", text_color=T.ERROR, font=T.font(12),
                           wraplength=400, justify="left", anchor="w")
        self.error.grid(row=6, column=0, columnspan=2, sticky="w")
        T.ghost_button(form, "Clear", self.clear_form).grid(
            row=7, column=0, sticky="ew", padx=(0, 6), pady=(6, 0))
        T.primary_button(form, "Register student", self.register_student).grid(
            row=7, column=1, sticky="ew", padx=(6, 0), pady=(6, 0))

    @property
    def _fields(self):
        return (self.f_id, self.f_prn, self.f_name, self.f_dept, self.f_class,
                self.f_div, self.f_email, self.f_mobile)

    # ---------------------------------------------------------------- camera
    def _build_camera(self, parent):
        card = Card(parent)
        card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=24)
        ctk.CTkLabel(body, text="Face scan", font=T.font(16, "bold"),
                     text_color=T.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(body, text="Look at the camera and slowly turn your head a little.",
                     font=T.font(12), text_color=T.TEXT_SECONDARY).pack(anchor="w", pady=(0, 12))
        self.camera = CameraView(body, width=440, height=310, on_frame=self._on_frame)
        self.camera.pack()
        self.progress = ctk.CTkProgressBar(body, height=8, progress_color=T.PRIMARY,
                                           fg_color=T.NEUTRAL_BG)
        self.progress.set(0)
        self.progress.pack(fill="x", pady=(14, 6))
        self.status = ctk.CTkLabel(body, text="Camera is off", font=T.font(12),
                                   text_color=T.TEXT_SECONDARY, anchor="w")
        self.status.pack(anchor="w")
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x", pady=(12, 0))
        row.columnconfigure((0, 1), weight=1, uniform="b")
        self.cam_btn = T.ghost_button(row, "Start camera", self.toggle_camera)
        self.cam_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.cap_btn = T.primary_button(row, "Capture face", self.start_capture, state="disabled")
        self.cap_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        self.preview = ctk.CTkLabel(body, text="", width=64, height=64)
        self.preview.pack(anchor="w", pady=(12, 0))

    def _on_frame(self, frame):
        self._frame_no += 1
        if self._frame_no % 2 == 0:
            self._faces = fe.detect_faces(frame)
        for (x, y, w, h) in self._faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (246, 93, 109), 3)
        return frame

    def toggle_camera(self):
        if self.camera.running:
            self.camera.stop()
            self._capturing = False
            self.cam_btn.configure(text="Start camera")
            self.cap_btn.configure(state="disabled")
            self.status.configure(text="Camera is off")
        elif self.camera.start():
            self.cam_btn.configure(text="Stop camera")
            self.cap_btn.configure(state="normal")
            self.status.configure(text="Camera ready — press “Capture face”.")
        else:
            self.status.configure(text="Camera unavailable.")

    def start_capture(self):
        if not self.camera.running:
            return
        self.samples, self.photo, self._capturing = [], None, True
        self._clear_preview()
        self.progress.set(0)
        self.cap_btn.configure(state="disabled")
        self.status.configure(text="Scanning… hold still, then turn slightly.")
        self._capture_tick(0)

    def _capture_tick(self, attempts):
        if not self._capturing:
            return
        frame = self.camera.last_frame
        box = fe.largest_face(fe.detect_faces(frame)) if frame is not None else None
        if box:
            self.samples.append(fe.crop_face(frame, box))
            if self.photo is None or len(self.samples) == SAMPLES_NEEDED // 2:
                self.photo = fe.crop_portrait(frame, box)
            self.progress.set(len(self.samples) / SAMPLES_NEEDED)
        if len(self.samples) >= SAMPLES_NEEDED:
            self._capturing = False
            self.cap_btn.configure(state="normal", text="Re-capture")
            self.status.configure(text=f"✓ Face captured ({len(self.samples)} samples).",
                                  text_color=T.SUCCESS)
            img = ctk.CTkImage(pil_from_bgr(self.photo, (64, 64)), size=(64, 64))
            self.preview.configure(image=img)
            self.preview._img = img
        elif attempts >= 80:
            self._capturing = False
            self.samples, self.photo = [], None
            self.progress.set(0)
            self.cap_btn.configure(state="normal")
            self.status.configure(text="No face found. Improve lighting and try again.",
                                  text_color=T.ERROR)
        else:
            self.after(180, lambda: self._capture_tick(attempts + 1))

    # -------------------------------------------------------------- register
    def _fail(self, message):
        self.error.configure(text=message)

    def register_student(self):
        sid, prn, name = self.f_id.get(), self.f_prn.get(), self.f_name.get()
        dept, cls, div = self.f_dept.get(), self.f_class.get(), self.f_div.get()
        email, mobile = self.f_email.get(), self.f_mobile.get()
        if not data.valid_student_id(sid):
            return self._fail("Student ID: 2-20 letters or numbers.")
        if not data.valid_prn(prn):
            return self._fail("PRN: 8-20 digits.")
        if not data.valid_name(name):
            return self._fail("Name: 2-50 letters and spaces.")
        if dept not in data.DEPARTMENTS:
            return self._fail("Please select a department.")
        if not cls or not div:
            return self._fail("Class and division are required.")
        if not data.valid_email(email):
            return self._fail("Enter a valid email address.")
        if not data.valid_mobile(mobile):
            return self._fail("Mobile: 10 digits starting with 6-9.")
        if len(self.samples) < SAMPLES_NEEDED or self.photo is None:
            return self._fail("Capture the student's face before registering.")

        filename = data.safe_photo_name(sid, name)
        student = {"student_id": sid, "prn": prn, "name": name, "department": dept,
                   "class": cls, "division": div, "email": email, "mobile": mobile,
                   "photo": filename}
        try:
            data.add_student(student)
        except ValueError as error:
            return self._fail(str(error))
        cv2.imwrite(os.path.join(data.PHOTO_DIR, filename), self.photo)
        fe.save_samples(sid, self.samples)
        trained = fe.train()
        self.clear_form()
        self._refresh_count()
        if fe.recognition_available():
            self.app.toast.show(f"✓ {name} registered · recogniser updated ({trained} trained).")
        else:
            self.app.toast.show(f"✓ {name} registered. Install opencv-contrib-python "
                                "to enable recognition.", "warning", 5000)

    def clear_form(self):
        for field in self._fields:
            field.clear()
        self.error.configure(text="")
        self.samples, self.photo, self._capturing = [], None, False
        self.progress.set(0)
        self._clear_preview()
        self.status.configure(text="Camera ready — press “Capture face”."
                              if self.camera.running else "Camera is off",
                              text_color=T.TEXT_SECONDARY)
        self.cap_btn.configure(text="Capture face",
                               state="normal" if self.camera.running else "disabled")

    def _clear_preview(self):
        img = blank_image(64, 64)
        self.preview.configure(image=img)
        self.preview._img = img

    def _refresh_count(self):
        text = f"{len(data.list_students())} registered"
        self.count_chip.configure(text=text, width=int(len(text) * 7.5) + 30)

    def on_show(self, **kwargs):
        self._refresh_count()

    def on_hide(self):
        self._capturing = False
        if self.camera.running:
            self.toggle_camera()


# ================================================================== directory
class StudentsPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.selected = None
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x", padx=32, pady=(28, 16))
        PageHeader(head, "Students", "Everyone registered with a face scan.").pack(side="left")
        T.ghost_button(head, "Retrain recogniser", self.retrain, width=170).pack(side="right")
        T.primary_button(head, "＋ Register", lambda: app.show("register"),
                         width=130).pack(side="right", padx=(0, 10))

        cols = ctk.CTkFrame(self, fg_color="transparent")
        cols.pack(fill="both", expand=True, padx=32, pady=(0, 24))
        cols.columnconfigure(0, weight=6, uniform="s")
        cols.columnconfigure(1, weight=4, uniform="s")
        cols.rowconfigure(0, weight=1)

        left = Card(cols)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.search = ctk.CTkEntry(left, height=42, corner_radius=10, border_color=T.BORDER,
                                   fg_color=T.INPUT_BG, text_color=T.TEXT_PRIMARY,
                                   placeholder_text="Search by ID, PRN or name…",
                                   font=T.font(13))
        self.search.pack(fill="x", padx=20, pady=(20, 12))
        self.search.bind("<KeyRelease>", lambda e: self.refresh())
        self.table = DataTable(left, [("id", "ID", 80), ("prn", "PRN", 110),
                                      ("name", "Name", 170), ("dept", "Department", 150),
                                      ("cls", "Class", 70)],
                               height=14, on_select=self.select_student)
        self.table.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.detail = Card(cols)
        self.detail.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self._render_detail(None)

    def refresh(self):
        students = data.search_students(self.search.get())
        self.table.set_rows([(s["student_id"], (s["student_id"], s["prn"], s["name"],
                                                s["department"], f'{s["class"]}-{s["division"]}'))
                             for s in students])

    def select_student(self, student_id):
        self.selected = data.get_student(student_id)
        self._render_detail(self.selected)

    def _render_detail(self, student):
        for child in self.detail.winfo_children():
            child.destroy()
        if not student:
            ctk.CTkLabel(self.detail, text="Select a student\nto see their profile.",
                         font=T.font(14), text_color=T.TEXT_SECONDARY
                         ).place(relx=0.5, rely=0.5, anchor="center")
            return
        body = ctk.CTkFrame(self.detail, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=24)
        avatar(body, student["name"], 120, data.photo_path(student)).pack(anchor="w")
        ctk.CTkLabel(body, text=student["name"], font=T.font(22, "bold"),
                     text_color=T.TEXT_PRIMARY).pack(anchor="w", pady=(14, 0))
        ctk.CTkLabel(body, text=student["department"], font=T.font(13),
                     text_color=T.TEXT_SECONDARY).pack(anchor="w", pady=(0, 14))
        for label, key in (("Student ID", "student_id"), ("PRN", "prn"), ("Email", "email"),
                           ("Mobile", "mobile"), ("Registered", "registered_date")):
            row = ctk.CTkFrame(body, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=label, width=90, anchor="w", font=T.font(12),
                         text_color=T.TEXT_SECONDARY).pack(side="left")
            ctk.CTkLabel(row, text=student.get(key, "-"), anchor="w", font=T.font(12, "bold"),
                         text_color=T.TEXT_PRIMARY).pack(side="left")
        T.primary_button(body, "View attendance", lambda: self.app.show(
            "attendance", student_id=student["student_id"])).pack(fill="x", pady=(18, 8))
        T.danger_button(body, "Delete student", self.delete_selected).pack(fill="x")

    def delete_selected(self):
        if not self.selected:
            return
        name = self.selected["name"]
        if not messagebox.askyesno("Delete student",
                                   f"Delete {name} and all of their attendance records?"):
            return
        data.delete_student(self.selected["student_id"])
        fe.train()
        self.selected = None
        self._render_detail(None)
        self.refresh()
        self.app.toast.show(f"{name} deleted.", "info")

    def retrain(self):
        if not fe.recognition_available():
            return self.app.toast.show("Install opencv-contrib-python for recognition.",
                                       "warning", 4500)
        count = fe.train()
        self.app.toast.show(f"Recogniser retrained on {count} student(s).", "success")

    def on_show(self, **kwargs):
        self.refresh()

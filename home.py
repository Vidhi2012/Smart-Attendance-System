"""Landing page."""
import tkinter as tk
import customtkinter as ctk
import theme as T
from widgets import Page, Card, Label

FEATURES = [
    ("Quick registration", "Add a student and scan their face in one short form."),
    ("Face recognition", "Students are identified on your webcam, not ticked by hand."),
    ("Automatic attendance", "Recognised students are marked present instantly, once per day."),
    ("History & records", "Look up any student and see every date and time they attended."),
    ("CSV export", "Download attendance for Excel or your college records."),
    ("Private by design", "All data stays on your computer. No cloud account needed."),
]
STEPS = [
    ("Register", "Enter details and scan the student's face."),
    ("Train", "The recogniser learns the new face automatically."),
    ("Recognise", "Start the camera at the beginning of a session."),
    ("Record", "Attendance is saved and ready to export."),
]


class HomePage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self._anim, self._dir, self._sections = None, 1, {}
        self._build_nav()
        self.body = ctk.CTkScrollableFrame(self, fg_color=T.APP_BG, corner_radius=0)
        self.body.pack(fill="both", expand=True)
        self._hero()
        self._sections["about"] = self._about()
        self._sections["features"] = self._features()
        self._sections["how"] = self._steps()
        self._cta()
        self._footer()

    # -------------------------------------------------------------------- nav
    def _build_nav(self):
        nav = ctk.CTkFrame(self, height=72, fg_color=T.CARD_BG, corner_radius=0)
        nav.pack(fill="x")
        nav.pack_propagate(False)
        logo = ctk.CTkFrame(nav, fg_color="transparent")
        logo.pack(side="left", padx=36)
        ctk.CTkLabel(logo, text="S", width=36, height=36, corner_radius=11,
                     fg_color=T.PRIMARY, text_color="white",
                     font=T.font(18, "bold")).pack(side="left")
        ctk.CTkLabel(logo, text=T.BRAND, font=T.font(20, "bold"),
                     text_color=T.TEXT_PRIMARY).pack(side="left", padx=10)

        right = ctk.CTkFrame(nav, fg_color="transparent")
        right.pack(side="right", padx=36)
        toggle = T.ghost_button(right, "", self.app.toggle_theme, width=44, height=38)
        toggle.pack(side="left", padx=(0, 8))
        self.app.register_theme_button(toggle, "icon")
        self.login_btn = T.ghost_button(right, "Log in", lambda: self.app.show("login"),
                                        width=96, height=38)
        self.login_btn.pack(side="left", padx=(0, 8))
        self.cta_btn = T.primary_button(right, "Get started",
                                        lambda: self.app.show("login", tab="signup"),
                                        width=124, height=38)
        self.cta_btn.pack(side="left")

        links = ctk.CTkFrame(nav, fg_color="transparent")
        links.pack(side="left", padx=20)
        for label, target in (("Home", "top"), ("About", "about"), ("Features", "features"),
                              ("How it works", "how"), ("Contact", "contact")):
            ctk.CTkButton(links, text=label, width=90, height=36, fg_color="transparent",
                          hover_color=T.PRIMARY_LIGHT, text_color=T.TEXT_SECONDARY,
                          font=T.font(13, "bold"),
                          command=lambda t=target: self._go(t)).pack(side="left")

    def _go(self, target):
        if target == "contact":
            return self.app.show("contact")
        self.update_idletasks()
        if target == "top":
            fraction = 0
        else:
            widget = self._sections[target]
            fraction = max(widget.winfo_y() - 10, 0) / max(self.body.winfo_height(), 1)
        try:
            self.body._parent_canvas.yview_moveto(fraction)
        except Exception:
            pass

    # ------------------------------------------------------------------- hero
    def _hero(self):
        hero = ctk.CTkFrame(self.body, fg_color="transparent")
        hero.pack(fill="x", padx=64, pady=(56, 40))
        hero.columnconfigure(0, weight=6, uniform="h")
        hero.columnconfigure(1, weight=5, uniform="h")
        left = ctk.CTkFrame(hero, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left, text="●  AI-POWERED ATTENDANCE", fg_color=T.PRIMARY_LIGHT,
                     text_color=T.PRIMARY, corner_radius=14, height=30, width=230,
                     font=T.font(11, "bold")).pack(anchor="w")
        Label(left, text="Attendance,\nrecognised at a glance.",
              font=T.font(48, "bold"), text_color=T.TEXT_PRIMARY,
              justify="left").pack(anchor="w", pady=(22, 14))
        Label(left, text="Register a face once. SmartMark recognises students on "
              "your webcam and records\ntheir attendance automatically — "
              "no registers, no proxies.", font=T.font(15),
              text_color=T.TEXT_SECONDARY, justify="left").pack(anchor="w")
        row = ctk.CTkFrame(left, fg_color="transparent")
        row.pack(anchor="w", pady=(28, 0))
        T.primary_button(row, "Register a student", lambda: self.app.show("register"),
                         width=190, height=48).pack(side="left")
        T.ghost_button(row, "Take attendance", lambda: self.app.show("attendance"),
                       width=170, height=48).pack(side="left", padx=12)

        self.canvas = tk.Canvas(hero, width=420, height=420, bg=T.c(T.APP_BG),
                                highlightthickness=0)
        self.canvas.grid(row=0, column=1, sticky="e")
        self._y = 100
        self._draw_scan()

    @staticmethod
    def _round_rect(c, x1, y1, x2, y2, r, **kw):
        pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
               x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        return c.create_polygon(pts, smooth=True, **kw)

    def _draw_scan(self):
        c, col = self.canvas, T.c
        c.delete("all")
        c.configure(bg=col(T.APP_BG))
        self._round_rect(c, 20, 20, 400, 400, 36, fill=col(T.HERO_CARD), outline="")
        c.create_oval(150, 100, 270, 220, fill=col(T.SIDEBAR_ACTIVE), outline="")
        c.create_arc(100, 230, 320, 450, start=0, extent=180, fill=col(T.SIDEBAR_ACTIVE),
                     outline="")
        for (x, y, dx, dy) in ((110, 80, 1, 1), (310, 80, -1, 1),
                               (110, 270, 1, -1), (310, 270, -1, -1)):
            c.create_line(x, y, x + 34 * dx, y, fill=col(T.PRIMARY), width=5, capstyle="round")
            c.create_line(x, y, x, y + 34 * dy, fill=col(T.PRIMARY), width=5, capstyle="round")
        self.scan_line = c.create_line(120, getattr(self, "_y", 100), 300,
                                       getattr(self, "_y", 100), fill=T.ACCENT, width=3)
        self._round_rect(c, 60, 318, 360, 376, 22, fill=col(T.CARD_BG), outline="")
        c.create_oval(76, 332, 104, 360, fill=col(T.SUCCESS_BG), outline="")
        c.create_text(90, 346, text="✓", fill=col(T.SUCCESS), font=T.font(13, "bold"))
        c.create_text(118, 335, text="Recognised", anchor="w", fill=col(T.TEXT_PRIMARY),
                      font=T.font(12, "bold"))
        c.create_text(118, 355, text="Marked present · just now", anchor="w",
                      fill=col(T.TEXT_SECONDARY), font=T.font(10))

    def on_theme(self):
        self._draw_scan()

    def _animate(self):
        self._y += 3 * self._dir
        if self._y >= 270 or self._y <= 100:
            self._dir *= -1
        self.canvas.coords(self.scan_line, 120, self._y, 300, self._y)
        self._anim = self.after(30, self._animate)

    # --------------------------------------------------------------- sections
    def _heading(self, title, subtitle):
        wrap = ctk.CTkFrame(self.body, fg_color="transparent")
        wrap.pack(fill="x", padx=64, pady=(48, 18))
        ctk.CTkLabel(wrap, text=title, font=T.font(30, "bold"),
                     text_color=T.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(wrap, text=subtitle, font=T.font(14),
                     text_color=T.TEXT_SECONDARY).pack(anchor="w", pady=(4, 0))
        return wrap

    def _about(self):
        wrap = self._heading("About SmartMark", "Built for classrooms that would rather teach.")
        card = Card(self.body)
        card.pack(fill="x", padx=64)
        Label(card, text="Paper registers are slow, error-prone and easy to game. "
                     "SmartMark replaces them with a contactless webcam workflow: students are "
                     "registered once with a short face scan, then recognised automatically at "
                     "the start of every session. Each check-in is stored with the student's "
                     "name, date and time, and can be reviewed or exported at any moment.",
                     font=T.font(14), text_color=T.TEXT_PRIMARY, wraplength=900,
                     justify="left").pack(anchor="w", padx=32, pady=28)
        return wrap

    def _features(self):
        wrap = self._heading("Everything you need", "A complete attendance toolkit.")
        grid = ctk.CTkFrame(self.body, fg_color="transparent")
        grid.pack(fill="x", padx=64)
        grid.columnconfigure((0, 1, 2), weight=1, uniform="f")
        for i, (title, text) in enumerate(FEATURES):
            card = Card(grid)
            card.grid(row=i // 3, column=i % 3, sticky="nsew", padx=6, pady=6)
            ctk.CTkLabel(card, text=f"{i + 1:02d}", font=T.font(12, "bold"),
                         text_color=T.PRIMARY, fg_color=T.PRIMARY_LIGHT, corner_radius=10,
                         width=36, height=28).pack(anchor="w", padx=20, pady=(20, 10))
            ctk.CTkLabel(card, text=title, font=T.font(15, "bold"),
                         text_color=T.TEXT_PRIMARY).pack(anchor="w", padx=20)
            Label(card, text=text, font=T.font(12), text_color=T.TEXT_SECONDARY,
                         wraplength=270, justify="left").pack(anchor="w", padx=20, pady=(4, 20))
        return wrap

    def _steps(self):
        wrap = self._heading("How it works", "From registration to records in four steps.")
        row = ctk.CTkFrame(self.body, fg_color="transparent")
        row.pack(fill="x", padx=64)
        row.columnconfigure(tuple(range(4)), weight=1, uniform="s")
        for i, (title, text) in enumerate(STEPS):
            card = Card(row)
            card.grid(row=0, column=i, sticky="nsew", padx=6)
            ctk.CTkLabel(card, text=str(i + 1), width=34, height=34, corner_radius=17,
                         fg_color=T.PRIMARY, text_color="white",
                         font=T.font(14, "bold")).pack(anchor="w", padx=18, pady=(18, 10))
            ctk.CTkLabel(card, text=title, font=T.font(15, "bold"),
                         text_color=T.TEXT_PRIMARY).pack(anchor="w", padx=18)
            Label(card, text=text, font=T.font(12), text_color=T.TEXT_SECONDARY,
                         wraplength=190, justify="left").pack(anchor="w", padx=18, pady=(4, 18))
        return wrap

    def _cta(self):
        band = ctk.CTkFrame(self.body, fg_color=T.BAND_BG, corner_radius=28)
        band.pack(fill="x", padx=64, pady=(56, 0))
        ctk.CTkLabel(band, text="Ready to retire the paper register?", font=T.font(28, "bold"),
                     text_color=T.TEXT_ON_DARK).pack(pady=(40, 6))
        ctk.CTkLabel(band, text="Create an account and register your first student in minutes.",
                     font=T.font(14), text_color=T.TEXT_ON_DARK_MUTED).pack()
        T.primary_button(band, "Start student registration",
                         lambda: self.app.show("register"), width=240,
                         height=48).pack(pady=(22, 40))

    def _footer(self):
        foot = ctk.CTkFrame(self.body, fg_color="transparent")
        foot.pack(fill="x", pady=(36, 28))
        ctk.CTkLabel(foot, text=f"{T.BRAND} · {T.TAGLINE}", font=T.font(13, "bold"),
                     text_color=T.TEXT_PRIMARY).pack()
        ctk.CTkLabel(foot, text="© 2026 SmartMark. All rights reserved.", font=T.font(11),
                     text_color=T.TEXT_SECONDARY).pack(pady=(2, 0))

    # -------------------------------------------------------------- lifecycle
    def on_show(self, **kwargs):
        if self.app.user:
            self.login_btn.configure(text="Dashboard",
                                     command=lambda: self.app.show("dashboard"))
            self.cta_btn.configure(text="Log out", command=self.app.logout)
        else:
            self.login_btn.configure(text="Log in", command=lambda: self.app.show("login"))
            self.cta_btn.configure(text="Get started",
                                   command=lambda: self.app.show("login", tab="signup"))
        if self._anim is None:
            self._animate()

    def on_hide(self):
        if self._anim is not None:
            self.after_cancel(self._anim)
            self._anim = None

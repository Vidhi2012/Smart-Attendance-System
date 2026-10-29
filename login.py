"""Login / sign-up screen."""
import customtkinter as ctk
import data
import theme as T
from widgets import Page, Field, Label


class AuthPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.columnconfigure(0, weight=5, uniform="a")
        self.columnconfigure(1, weight=6, uniform="a")
        self.rowconfigure(0, weight=1)
        self._build_brand_panel()
        self._build_form_panel()

    # ------------------------------------------------------------- brand side
    def _build_brand_panel(self):
        panel = ctk.CTkFrame(self, fg_color=T.SIDEBAR_BG, corner_radius=0)
        panel.grid(row=0, column=0, sticky="nsew")
        inner = ctk.CTkFrame(panel, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(inner, text="S", width=54, height=54, corner_radius=16,
                     fg_color=T.PRIMARY, text_color="white",
                     font=T.font(26, "bold")).pack(anchor="w")
        ctk.CTkLabel(inner, text=T.BRAND, font=T.font(34, "bold"),
                     text_color=T.TEXT_ON_DARK).pack(anchor="w", pady=(18, 0))
        Label(inner, text="Attendance that takes\ncare of itself.",
              font=T.font(20), text_color=T.TEXT_ON_DARK_MUTED,
              justify="left").pack(anchor="w", pady=(6, 28))
        for line in ("Register a face once", "Recognise students on camera",
                     "Records, history and CSV export"):
            row = ctk.CTkFrame(inner, fg_color="transparent")
            row.pack(anchor="w", pady=5)
            ctk.CTkLabel(row, text="✓", width=26, height=26, corner_radius=13,
                         fg_color=T.SIDEBAR_ACTIVE, text_color=T.ACCENT,
                         font=T.font(12, "bold")).pack(side="left")
            ctk.CTkLabel(row, text=line, font=T.font(14),
                         text_color=T.TEXT_ON_DARK).pack(side="left", padx=12)

    # -------------------------------------------------------------- form side
    def _build_form_panel(self):
        side = ctk.CTkFrame(self, fg_color=T.APP_BG, corner_radius=0)
        side.grid(row=0, column=1, sticky="nsew")
        ctk.CTkButton(side, text="← Back to home", width=130, height=34,
                      fg_color="transparent", hover_color=T.PRIMARY_LIGHT,
                      text_color=T.TEXT_SECONDARY, font=T.font(12, "bold"),
                      command=lambda: self.app.show("home")
                      ).place(x=24, y=20)

        toggle = T.ghost_button(side, "", self.app.toggle_theme, width=44, height=34)
        toggle.place(relx=1.0, x=-24, y=20, anchor="ne")
        self.app.register_theme_button(toggle, "icon")

        card = ctk.CTkFrame(side, fg_color=T.CARD_BG, corner_radius=24,
                            border_width=1, border_color=T.BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center")
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(padx=44, pady=36)

        self.title = ctk.CTkLabel(body, text="Welcome back", font=T.font(28, "bold"),
                                  text_color=T.TEXT_PRIMARY)
        self.title.pack(anchor="w")
        self.subtitle = ctk.CTkLabel(body, text="Log in to manage attendance.",
                                     font=T.font(13), text_color=T.TEXT_SECONDARY)
        self.subtitle.pack(anchor="w", pady=(2, 18))

        self.tabs = ctk.CTkSegmentedButton(
            body, values=["Log in", "Sign up"], command=self._switch, height=40,
            corner_radius=12, fg_color=T.NEUTRAL_BG, selected_color=T.PRIMARY,
            selected_hover_color=T.PRIMARY_HOVER, unselected_color=T.NEUTRAL_BG,
            unselected_hover_color=T.PRIMARY_LIGHT, text_color=T.TEXT_PRIMARY,
            font=T.font(13, "bold"))
        self.tabs.pack(fill="x")
        self.tabs.set("Log in")

        self.stage = ctk.CTkFrame(body, fg_color="transparent", width=460)
        self.stage.pack(fill="x", pady=(18, 0))
        self.login_form = self._login_form(self.stage)
        self.signup_form = self._signup_form(self.stage)
        self.login_form.pack(fill="x")

        self.error = Label(body, text="", text_color=T.ERROR, font=T.font(12),
                           wraplength=440, justify="left", anchor="w")
        self.error.pack(anchor="w", pady=(10, 0))

    def _login_form(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        self.login_email = Field(f, "Email", "you@college.edu")
        self.login_email.pack(fill="x", pady=(0, 12))
        self.login_password = Field(f, "Password", "Your password", show="•")
        self.login_password.pack(fill="x")
        self.show_pw = ctk.CTkCheckBox(
            f, text="Show password", font=T.font(12), text_color=T.TEXT_SECONDARY,
            fg_color=T.PRIMARY, hover_color=T.PRIMARY_HOVER, border_color=T.BORDER,
            checkbox_width=18, checkbox_height=18, command=self._toggle_password)
        self.show_pw.pack(anchor="w", pady=(10, 14))
        T.primary_button(f, "Log in", self.login).pack(fill="x")
        self.login_password.widget.bind("<Return>", lambda e: self.login())
        return f

    def _signup_form(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.columnconfigure((0, 1), weight=1, uniform="s")
        self.su_name = Field(f, "Full name", "Aarav Sharma")
        self.su_id = Field(f, "Staff ID", "STF001")
        self.su_email = Field(f, "Email", "you@college.edu")
        self.su_role = Field(f, "Role", "Select role", values=data.ROLES)
        self.su_dept = Field(f, "Department", "Select department", values=data.DEPARTMENTS)
        self.su_pw = Field(f, "Password", "Min 8 chars", show="•")
        self.su_pw2 = Field(f, "Confirm password", "Repeat password", show="•")
        self.su_name.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=(0, 10))
        self.su_id.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=(0, 10))
        self.su_email.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.su_role.grid(row=2, column=0, sticky="ew", padx=(0, 8), pady=(0, 10))
        self.su_dept.grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=(0, 10))
        self.su_pw.grid(row=3, column=0, sticky="ew", padx=(0, 8), pady=(0, 14))
        self.su_pw2.grid(row=3, column=1, sticky="ew", padx=(8, 0), pady=(0, 14))
        T.primary_button(f, "Create account", self.signup).grid(
            row=4, column=0, columnspan=2, sticky="ew")
        return f

    # ---------------------------------------------------------------- actions
    def _switch(self, value):
        self.error.configure(text="")
        if value == "Log in":
            self.signup_form.pack_forget()
            self.login_form.pack(fill="x")
            self.title.configure(text="Welcome back")
            self.subtitle.configure(text="Log in to manage attendance.")
        else:
            self.login_form.pack_forget()
            self.signup_form.pack(fill="x")
            self.title.configure(text="Create your account")
            self.subtitle.configure(text="For faculty and administrators. Takes a minute.")

    def _toggle_password(self):
        self.login_password.widget.configure(show="" if self.show_pw.get() else "•")

    def _fail(self, message):
        self.error.configure(text=message)

    def login(self):
        email, password = self.login_email.get(), self.login_password.get()
        if not email or not data.valid_email(email):
            return self._fail("Enter a valid email address.")
        if not password:
            return self._fail("Password is required.")
        user = data.authenticate(email, password)
        if user is None:
            return self._fail("Invalid email or password.")
        self.error.configure(text="")
        self.login_password.clear()
        self.app.login(user)

    def signup(self):
        name, uid, email = self.su_name.get(), self.su_id.get(), self.su_email.get()
        role, dept = self.su_role.get(), self.su_dept.get()
        pw, pw2 = self.su_pw.get(), self.su_pw2.get()
        if not data.valid_full_name(name):
            return self._fail("Enter your full name using letters and spaces only.")
        if not data.valid_user_id(uid):
            return self._fail("ID must be 3-20 letters, numbers, _ or -.")
        if not data.valid_email(email):
            return self._fail("Enter a valid email address.")
        if role not in data.ROLES:
            return self._fail("Please select a role.")
        if dept not in data.DEPARTMENTS:
            return self._fail("Please select a department.")
        if not data.valid_password(pw):
            return self._fail("Password needs 8+ characters with a letter, "
                              "a number and a symbol.")
        if pw != pw2:
            return self._fail("Passwords do not match.")
        try:
            data.create_user(name, uid, email, role, dept, pw)
        except ValueError as error:
            return self._fail(str(error))
        for field in (self.su_name, self.su_id, self.su_email, self.su_pw, self.su_pw2,
                      self.su_role, self.su_dept):
            field.clear()
        self.tabs.set("Log in")
        self._switch("Log in")
        self.login_email.set(email)
        self.app.toast.show("Account created — please log in.", "success")

    def on_show(self, **kwargs):
        self.error.configure(text="")
        if kwargs.get("tab") == "signup":
            self.tabs.set("Sign up")
            self._switch("Sign up")

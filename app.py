"""SmartMark - AI Smart Attendance System.  Run:  python app.py"""
import customtkinter as ctk
import data
import theme as T
from widgets import Toast, initials, refresh_tables
from home import HomePage
from login import AuthPage
from contact import ContactPage
from main import RegistrationPage, StudentsPage
from Attendance_dashboard import OverviewPage, AttendancePage

PAGES = {
    "home": HomePage, "login": AuthPage, "contact": ContactPage,
    "dashboard": OverviewPage, "attendance": AttendancePage,
    "register": RegistrationPage, "students": StudentsPage,
}
PROTECTED = {"dashboard", "attendance", "register", "students"}
PUBLIC_NO_SIDEBAR = {"home", "login"}
NAV = [("dashboard", "⌂", "Dashboard"), ("attendance", "◉", "Attendance"),
       ("register", "＋", "Register"), ("students", "☷", "Students"),
       ("contact", "✉", "Support")]


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, width=240, corner_radius=0, fg_color=T.SIDEBAR_BG)
        self.app = app
        self.pack_propagate(False)
        logo = ctk.CTkFrame(self, fg_color="transparent")
        logo.pack(anchor="w", padx=24, pady=(28, 24))
        ctk.CTkLabel(logo, text="S", width=38, height=38, corner_radius=12,
                     fg_color=T.PRIMARY, text_color="white",
                     font=T.font(19, "bold")).pack(side="left")
        ctk.CTkLabel(logo, text=T.BRAND, font=T.font(19, "bold"),
                     text_color=T.TEXT_ON_DARK).pack(side="left", padx=10)
        self.buttons = {}
        for key, glyph, label in NAV:
            btn = ctk.CTkButton(self, text=f"  {glyph}   {label}", anchor="w", height=44,
                                corner_radius=12, fg_color="transparent",
                                hover_color=T.SIDEBAR_HOVER, text_color=T.TEXT_ON_DARK_MUTED,
                                font=T.font(14, "bold"),
                                command=lambda k=key: app.show(k))
            btn.pack(fill="x", padx=14, pady=2)
            self.buttons[key] = btn

        self.user_card = ctk.CTkFrame(self, fg_color=T.SIDEBAR_HOVER, corner_radius=16)
        self.user_card.pack(side="bottom", fill="x", padx=14, pady=16)
        self.avatar = ctk.CTkLabel(self.user_card, text="?", width=38, height=38,
                                   corner_radius=19, fg_color=T.PRIMARY, text_color="white",
                                   font=T.font(13, "bold"))
        self.avatar.pack(side="left", padx=(12, 10), pady=12)
        info = ctk.CTkFrame(self.user_card, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)
        self.name = ctk.CTkLabel(info, text="", font=T.font(12, "bold"),
                                 text_color=T.TEXT_ON_DARK, anchor="w")
        self.name.pack(anchor="w")
        self.role = ctk.CTkLabel(info, text="", font=T.font(11),
                                 text_color=T.TEXT_ON_DARK_MUTED, anchor="w")
        self.role.pack(anchor="w")
        ctk.CTkButton(self.user_card, text="⏻", width=34, height=34, corner_radius=10,
                      fg_color="transparent", hover_color=T.SIDEBAR_ACTIVE,
                      text_color=T.TEXT_ON_DARK_MUTED, font=T.font(15),
                      command=app.logout).pack(side="right", padx=8)
        ctk.CTkButton(self, text="←  Home page", anchor="w", height=36, corner_radius=10,
                      fg_color="transparent", hover_color=T.SIDEBAR_HOVER,
                      text_color=T.TEXT_ON_DARK_MUTED, font=T.font(12),
                      command=lambda: app.show("home")).pack(side="bottom", fill="x", padx=14)
        theme_btn = ctk.CTkButton(self, text="", anchor="w", height=36, corner_radius=10,
                                  fg_color="transparent", hover_color=T.SIDEBAR_HOVER,
                                  text_color=T.TEXT_ON_DARK_MUTED, font=T.font(12),
                                  command=app.toggle_theme)
        theme_btn.pack(side="bottom", fill="x", padx=14)
        app.register_theme_button(theme_btn, "full")

    def set_user(self, user):
        self.avatar.configure(text=initials(user["full_name"]))
        self.name.configure(text=user["full_name"])
        self.role.configure(text=f'{user["role"]} · {user["department"]}')

    def set_active(self, name):
        for key, btn in self.buttons.items():
            active = key == name
            btn.configure(fg_color=T.SIDEBAR_ACTIVE if active else "transparent",
                          text_color=T.TEXT_ON_DARK if active else T.TEXT_ON_DARK_MUTED)


class App(ctk.CTk):
    def __init__(self):
        T.set_mode(data.get_setting("theme", "light"))   # restore saved choice
        self._theme_btns = []
        super().__init__(fg_color=T.APP_BG)
        self.title(f"{T.BRAND} — {T.TAGLINE}")
        self.geometry("1320x840")
        self.minsize(1180, 760)
        T.style_treeview()
        self.user, self.current, self.current_name = None, None, None
        self._pending, self._previous = None, "home"
        self.pages = {}

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.sidebar = Sidebar(self, self)
        self.content = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.toast = Toast(self.content)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.show("home")

    # ------------------------------------------------------------------- theme
    def register_theme_button(self, button, style="full"):
        """Buttons registered here always show the action they will perform."""
        self._theme_btns.append((button, style))
        self._update_theme_buttons()

    def _update_theme_buttons(self):
        dark = T.is_dark()
        for button, style in self._theme_btns:
            if style == "icon":
                button.configure(text="☀" if dark else "☾")
            else:
                button.configure(text="  ☀   Light mode" if dark else "  ☾   Dark mode")

    def toggle_theme(self):
        new = "light" if T.is_dark() else "dark"
        T.set_mode(new)
        data.set_setting("theme", new)
        T.style_treeview()
        refresh_tables()
        for page in self.pages.values():
            if hasattr(page, "on_theme"):
                page.on_theme()
        self._update_theme_buttons()

    # ----------------------------------------------------------------- routing
    def show(self, name, **kwargs):
        if name in PROTECTED and not self.user:
            self._pending = (name, kwargs)         # resume here after login
            name, kwargs = "login", {}
        if self.current is not None:
            self.current.on_hide()
            self.current.pack_forget()
            if self.current_name not in PUBLIC_NO_SIDEBAR:
                self._previous = self.current_name
            elif self.current_name == "home":
                self._previous = "home"
        if name not in self.pages:
            self.pages[name] = PAGES[name](self.content, self)
        page = self.pages[name]
        page.pack(fill="both", expand=True)
        self.current, self.current_name = page, name

        if self.user and name not in PUBLIC_NO_SIDEBAR:
            self.sidebar.grid(row=0, column=0, sticky="ns")
            self.sidebar.set_active(name)
        else:
            self.sidebar.grid_remove()
        page.on_show(**kwargs)
        self.toast.lift()

    def go_back(self):
        """Used by the Contact page's back button."""
        target = self._previous if self.user and self._previous != "contact" else "home"
        self.show(target if target in PAGES else "home")

    # -------------------------------------------------------------------- auth
    def login(self, user):
        self.user = user
        self.sidebar.set_user(user)
        name, kwargs = self._pending or ("dashboard", {})
        self._pending = None
        self.show(name, **kwargs)
        self.toast.show(f'Welcome, {user["full_name"].split()[0]}!', "success")

    def logout(self):
        self.user, self._pending = None, None
        self.show("home")
        self.toast.show("You have been logged out.", "info")

    def on_close(self):
        if self.current is not None:
            self.current.on_hide()      # releases the camera
        self.destroy()


if __name__ == "__main__":
    App().mainloop()

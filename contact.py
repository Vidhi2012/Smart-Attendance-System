"""Support / contact screen."""
import customtkinter as ctk
import data
import theme as T
from widgets import Page, Card, Field, Label

# Placeholder details - replace with your institution's real contact info.
SUPPORT_EMAIL = "support@smartmark.app"
SUPPORT_HOURS = "Mon - Fri  |  9:00 AM - 6:00 PM"


class ContactPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.columnconfigure(0, weight=4, uniform="c")
        self.columnconfigure(1, weight=6, uniform="c")
        self.rowconfigure(0, weight=1)
        self._build_info()
        self._build_form()

    def _build_info(self):
        panel = ctk.CTkFrame(self, fg_color=T.SIDEBAR_BG, corner_radius=24)
        panel.grid(row=0, column=0, sticky="nsew", padx=(32, 12), pady=32)
        ctk.CTkButton(panel, text="← Back", width=80, height=32, fg_color="transparent",
                      hover_color=T.SIDEBAR_HOVER, text_color=T.TEXT_ON_DARK_MUTED,
                      font=T.font(12, "bold"), command=self.app.go_back
                      ).pack(anchor="w", padx=20, pady=(20, 0))
        ctk.CTkLabel(panel, text="Get in touch", font=T.font(30, "bold"),
                     text_color=T.TEXT_ON_DARK).pack(anchor="w", padx=32, pady=(18, 4))
        Label(panel, text="Questions, feedback or a feature idea?\nWe read every message.",
              font=T.font(13), text_color=T.TEXT_ON_DARK_MUTED,
              justify="left").pack(anchor="w", padx=32, pady=(0, 28))
        for title, value in (("EMAIL", SUPPORT_EMAIL), ("HOURS", SUPPORT_HOURS)):
            ctk.CTkLabel(panel, text=title, font=T.font(10, "bold"),
                         text_color=T.ACCENT).pack(anchor="w", padx=32)
            ctk.CTkLabel(panel, text=value, font=T.font(14),
                         text_color=T.TEXT_ON_DARK).pack(anchor="w", padx=32, pady=(0, 18))

    def _build_form(self):
        card = Card(self)
        card.grid(row=0, column=1, sticky="nsew", padx=(12, 32), pady=32)
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=40, pady=36)
        ctk.CTkLabel(body, text="Send a message", font=T.font(24, "bold"),
                     text_color=T.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(body, text="All fields are required.", font=T.font(13),
                     text_color=T.TEXT_SECONDARY).pack(anchor="w", pady=(2, 20))
        self.email = Field(body, "Your email", "you@example.com")
        self.email.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(body, text="Message", font=T.font(12, "bold"),
                     text_color=T.TEXT_PRIMARY).pack(anchor="w", pady=(0, 4))
        self.message = ctk.CTkTextbox(body, height=190, corner_radius=10, border_width=1,
                                      border_color=T.BORDER, fg_color=T.INPUT_BG,
                                      text_color=T.TEXT_PRIMARY, font=T.font(13))
        self.message.pack(fill="x")
        self.error = ctk.CTkLabel(body, text="", text_color=T.ERROR, font=T.font(12),
                                  anchor="w")
        self.error.pack(anchor="w", pady=(10, 0))
        T.primary_button(body, "Send message", self.send_message, width=180).pack(anchor="w", pady=(8, 0))

    def send_message(self):
        email, message = self.email.get(), self.message.get("1.0", "end").strip()
        if not data.valid_email(email):
            return self.error.configure(text="Enter a valid email address.")
        if len(message) < 10:
            return self.error.configure(text="Message must be at least 10 characters.")
        data.save_message(email, message)
        self.error.configure(text="")
        self.email.clear()
        self.message.delete("1.0", "end")
        self.app.toast.show("Message saved — thank you!", "success")

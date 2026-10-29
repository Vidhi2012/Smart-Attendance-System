"""SmartMark design system. Every colour is a (light, dark) pair, so CustomTkinter
widgets switch automatically when the appearance mode changes."""
import sys
import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ---- Surfaces (light, dark) ------------------------------------------------
APP_BG = ("#F6F5FB", "#0F0E1A")
CARD_BG = ("#FFFFFF", "#181628")
SIDEBAR_BG = ("#14112B", "#0B0A18")
SIDEBAR_HOVER = ("#221E45", "#1B1833")
SIDEBAR_ACTIVE = ("#2D2760", "#2A2459")
INK = ("#0E0C1F", "#07060F")             # camera backdrop
BAND_BG = ("#14112B", "#221E45")         # call-to-action band
HERO_CARD = ("#14112B", "#1E1B3A")

# ---- Brand -----------------------------------------------------------------
PRIMARY = ("#6D5DF6", "#7C6CF8")
PRIMARY_HOVER = ("#5B4AE5", "#6A59EE")
PRIMARY_LIGHT = ("#ECE9FF", "#2A2459")
ACCENT = "#F472B6"

# ---- Text ------------------------------------------------------------------
TEXT_PRIMARY = ("#17142B", "#F1F0FA")
TEXT_SECONDARY = ("#6B6885", "#A09DC0")
TEXT_ON_DARK = "#F8FAFC"
TEXT_ON_DARK_MUTED = "#A9A5C9"

# ---- Lines & states --------------------------------------------------------
BORDER = ("#E9E7F5", "#2A2745")
INPUT_BG = ("#FFFFFF", "#201D35")
NEUTRAL_BG = ("#F1F0F9", "#211E36")
ROW_ALT = ("#FAF9FE", "#1C1A2F")
SUCCESS = ("#15803D", "#4ADE80")
SUCCESS_BG = ("#DCFCE7", "#14352A")
WARNING = ("#B45309", "#FBBF24")
WARNING_BG = ("#FEF3C7", "#3A2E10")
ERROR = ("#B91C1C", "#F87171")
ERROR_BG = ("#FEE2E2", "#3D1B22")
ERROR_HOVER = ("#FECACA", "#4B2430")
AMBER = "#F59E0B"

BRAND = "SmartMark"
TAGLINE = "AI Smart Attendance"

if sys.platform.startswith("win"):
    FAMILY = "Segoe UI"
elif sys.platform == "darwin":
    FAMILY = "Helvetica Neue"
else:
    FAMILY = "DejaVu Sans"


def font(size=13, weight="normal"):
    return (FAMILY, size, weight)


# ---- Light / dark mode -----------------------------------------------------
def mode():
    """'Light' or 'Dark'."""
    return ctk.get_appearance_mode()


def is_dark():
    return mode() == "Dark"


def set_mode(name):
    ctk.set_appearance_mode("dark" if str(name).lower() == "dark" else "light")


def c(color):
    """Resolve a (light, dark) pair to a plain colour for widgets that can't take
    pairs (tk.Canvas, ttk styles)."""
    if isinstance(color, (tuple, list)):
        return color[1] if is_dark() else color[0]
    return color


# ---- Button factories ------------------------------------------------------
def primary_button(parent, text, command, **kw):
    kw.setdefault("height", 42)
    return ctk.CTkButton(
        parent, text=text, command=command, fg_color=PRIMARY,
        hover_color=PRIMARY_HOVER, text_color="#FFFFFF", corner_radius=12,
        font=font(13, "bold"), **kw)


def ghost_button(parent, text, command, **kw):
    kw.setdefault("height", 42)
    return ctk.CTkButton(
        parent, text=text, command=command, fg_color="transparent",
        hover_color=PRIMARY_LIGHT, text_color=PRIMARY, border_width=1,
        border_color=BORDER, corner_radius=12, font=font(13, "bold"), **kw)


def danger_button(parent, text, command, **kw):
    kw.setdefault("height", 42)
    return ctk.CTkButton(
        parent, text=text, command=command, fg_color=ERROR_BG,
        hover_color=ERROR_HOVER, text_color=ERROR, corner_radius=12,
        font=font(13, "bold"), **kw)


def style_treeview():
    """Flat modern ttk.Treeview. Call after the root exists and again on theme change."""
    from tkinter import ttk
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure("Smart.Treeview", background=c(CARD_BG), fieldbackground=c(CARD_BG),
                    foreground=c(TEXT_PRIMARY), rowheight=38, borderwidth=0,
                    font=(FAMILY, 11))
    style.configure("Smart.Treeview.Heading", background=c(NEUTRAL_BG),
                    foreground=c(TEXT_SECONDARY), font=(FAMILY, 10, "bold"),
                    relief="flat", borderwidth=0, padding=(8, 8))
    style.map("Smart.Treeview",
              background=[("selected", c(PRIMARY_LIGHT))],
              foreground=[("selected", c(PRIMARY))])
    style.layout("Smart.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

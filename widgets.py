"""Reusable UI building blocks shared by every page."""
import sys
import weakref
import tkinter as tk
from tkinter import ttk
import cv2
import customtkinter as ctk
from PIL import Image
import theme as T


class Card(ctk.CTkFrame):
    def __init__(self, parent, **kw):
        kw.setdefault("fg_color", T.CARD_BG)
        kw.setdefault("corner_radius", 18)
        kw.setdefault("border_width", 1)
        kw.setdefault("border_color", T.BORDER)
        super().__init__(parent, **kw)


class PageHeader(ctk.CTkFrame):
    def __init__(self, parent, title, subtitle=""):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(self, text=title, font=T.font(26, "bold"),
                     text_color=T.TEXT_PRIMARY, anchor="w").pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(self, text=subtitle, font=T.font(13),
                         text_color=T.TEXT_SECONDARY, anchor="w").pack(anchor="w", pady=(2, 0))


class StatCard(Card):
    """Big number with a caption, e.g. 'Present today'."""
    def __init__(self, parent, label, value="0", tint=T.PRIMARY, tint_bg=T.PRIMARY_LIGHT):
        super().__init__(parent)
        bar = ctk.CTkFrame(self, width=36, height=6, corner_radius=3, fg_color=tint)
        bar.pack(anchor="w", padx=20, pady=(18, 0))
        self.value = ctk.CTkLabel(self, text=str(value), font=T.font(30, "bold"),
                                  text_color=T.TEXT_PRIMARY, anchor="w")
        self.value.pack(anchor="w", padx=20, pady=(8, 0))
        ctk.CTkLabel(self, text=label, font=T.font(12), text_color=T.TEXT_SECONDARY,
                     anchor="w").pack(anchor="w", padx=20, pady=(0, 18))

    def set(self, value):
        self.value.configure(text=str(value))


class Field(ctk.CTkFrame):
    """Label + entry (optionally a password entry or dropdown)."""
    def __init__(self, parent, label, placeholder="", show=None, values=None):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(self, text=label, font=T.font(12, "bold"),
                     text_color=T.TEXT_PRIMARY, anchor="w").pack(anchor="w", pady=(0, 4))
        self.values = values
        if values:
            self.widget = ctk.CTkOptionMenu(
                self, values=values, height=42, corner_radius=10,
                fg_color=T.INPUT_BG, button_color=T.PRIMARY_LIGHT,
                button_hover_color=T.BORDER, text_color=T.TEXT_PRIMARY,
                dropdown_fg_color=T.CARD_BG, dropdown_text_color=T.TEXT_PRIMARY,
                dropdown_hover_color=T.PRIMARY_LIGHT, font=T.font(13),
                dropdown_font=T.font(13), anchor="w")
            self.widget.set(placeholder or values[0])
            self.placeholder = placeholder or values[0]
        else:
            self.widget = ctk.CTkEntry(
                self, height=42, corner_radius=10, fg_color=T.INPUT_BG,
                border_color=T.BORDER, border_width=1, text_color=T.TEXT_PRIMARY,
                placeholder_text=placeholder, placeholder_text_color="#A09DB8",
                font=T.font(13), show=show)
        self.widget.pack(fill="x")

    def get(self):
        return self.widget.get().strip() if not self.values else self.widget.get()

    def set(self, value):
        if self.values:
            self.widget.set(value)
        else:
            self.widget.delete(0, "end")
            self.widget.insert(0, value)

    def clear(self):
        if self.values:
            self.widget.set(self.placeholder)
        else:
            self.widget.delete(0, "end")

    def focus(self):
        if not self.values:
            self.widget.focus()


_TABLES = weakref.WeakSet()


def refresh_tables():
    """Re-apply row colours after a light/dark switch."""
    for table in list(_TABLES):
        table.apply_tags()


class DataTable(ctk.CTkFrame):
    """Styled ttk.Treeview with a scrollbar. columns = [(key, heading, width)]."""
    def __init__(self, parent, columns, height=8, on_select=None):
        super().__init__(parent, fg_color="transparent")
        self.tree = ttk.Treeview(self, columns=[c[0] for c in columns],
                                 show="headings", style="Smart.Treeview",
                                 height=height, selectmode="browse")
        for key, heading, width in columns:
            self.tree.heading(key, text=heading, anchor="w")
            self.tree.column(key, width=width, anchor="w", stretch=True)
        bar = ctk.CTkScrollbar(self, command=self.tree.yview, width=12)
        self.tree.configure(yscrollcommand=bar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        bar.pack(side="right", fill="y", padx=(6, 0))
        self.apply_tags()
        _TABLES.add(self)
        self._on_select = on_select
        if on_select:
            self.tree.bind("<<TreeviewSelect>>", self._selected)

    def apply_tags(self):
        self.tree.tag_configure("odd", background=T.c(T.ROW_ALT))
        self.tree.tag_configure("even", background=T.c(T.CARD_BG))

    def _selected(self, _event=None):
        sel = self.tree.selection()
        if sel and self._on_select:
            self._on_select(sel[0])

    def set_rows(self, rows):
        """rows = [(iid, values_tuple), ...]"""
        self.tree.delete(*self.tree.get_children())
        for i, (iid, values) in enumerate(rows):
            self.tree.insert("", "end", iid=str(iid), values=values,
                             tags=("odd" if i % 2 else "even",))


class Toast(ctk.CTkLabel):
    """Small non-blocking message that fades after a moment."""
    def __init__(self, parent):
        super().__init__(parent, text="", corner_radius=12, font=T.font(13, "bold"),
                         height=44)
        self._job = None

    def show(self, message, kind="success", ms=3200):
        palette = {"success": (T.SUCCESS_BG, T.SUCCESS), "error": (T.ERROR_BG, T.ERROR),
                   "warning": (T.WARNING_BG, T.WARNING), "info": (T.PRIMARY_LIGHT, T.PRIMARY)}
        bg, fg = palette.get(kind, palette["info"])
        self.configure(text=message, fg_color=bg, text_color=fg,
                       width=min(len(message) * 8 + 44, 760))
        self.place(relx=0.5, rely=0.96, anchor="s")
        self.lift()
        if self._job:
            self.after_cancel(self._job)
        self._job = self.after(ms, self.place_forget)


class CameraView(ctk.CTkFrame):
    """Live webcam preview rendered inside the window (no pop-up cv2 window).

    on_frame(frame_bgr) may draw on the frame and return it to be displayed.
    """
    def __init__(self, parent, width=560, height=400, on_frame=None, mirror=True):
        super().__init__(parent, fg_color=T.INK, corner_radius=18,
                         width=width, height=height)
        self.pack_propagate(False)
        self._cw, self._ch = width, height
        self.on_frame, self.mirror = on_frame, mirror
        self.cap, self.running, self.last_frame = None, False, None
        self._job, self._img = None, None
        self.view = ctk.CTkLabel(self, text="Camera is off", text_color="#8D89B3",
                                 font=T.font(14))
        self.view.pack(expand=True, fill="both")
        self._blank("Camera is off")

    def _blank(self, text):
        img = ctk.CTkImage(Image.new("RGB", (self._cw, self._ch), (14, 12, 31)),
                           size=(self._cw, self._ch))
        self._img = img
        self.view.configure(image=img, text=text)

    def start(self):
        if self.running:
            return True
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) if sys.platform.startswith("win") \
            else cv2.VideoCapture(0)
        if not cap.isOpened():
            cap.release()
            cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            cap.release()
            self._blank("Camera unavailable.\nCheck that it is connected and allowed.")
            return False
        self.cap, self.running = cap, True
        self._tick()
        return True

    def _tick(self):
        if not self.running:
            return
        ok, frame = self.cap.read()
        if ok:
            if self.mirror:
                frame = cv2.flip(frame, 1)
            self.last_frame = frame.copy()
            shown = frame
            if self.on_frame:
                try:
                    out = self.on_frame(frame)
                    shown = out if out is not None else frame
                except Exception as error:  # keep the preview alive
                    print("on_frame error:", error)
            self._render(shown)
        self._job = self.after(30, self._tick)

    def _render(self, bgr):
        h, w = bgr.shape[:2]
        tw, th = max(self.winfo_width(), 50), max(self.winfo_height(), 50)
        scale = min(tw / w, th / h)
        nw, nh = max(int(w * scale), 1), max(int(h * scale), 1)
        rgb = cv2.cvtColor(cv2.resize(bgr, (nw, nh)), cv2.COLOR_BGR2RGB)
        img = ctk.CTkImage(Image.fromarray(rgb), size=(nw, nh))
        self._img = img
        self.view.configure(image=img, text="")

    def stop(self):
        self.running = False
        if self._job:
            try:
                self.after_cancel(self._job)
            except Exception:
                pass
            self._job = None
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.last_frame = None
        self._blank("Camera is off")


class Page(ctk.CTkFrame):
    """Base class for every screen. The App calls on_show / on_hide."""
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app

    def on_show(self, **kwargs):
        pass

    def on_hide(self):
        pass


def pil_from_bgr(bgr, size=None):
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb)
    return img.resize(size) if size else img


def initials(name):
    parts = [p for p in name.split() if p]
    return "".join(p[0] for p in parts[:2]).upper() or "?"


def avatar(parent, name, size=64, photo=None):
    """Round-ish avatar: student photo if present, otherwise initials."""
    if photo:
        try:
            img = ctk.CTkImage(Image.open(photo).convert("RGB").resize((size, size)),
                               size=(size, size))
            lbl = ctk.CTkLabel(parent, text="", image=img, width=size, height=size,
                               corner_radius=size // 4)
            lbl._img = img
            return lbl
        except Exception:
            pass
    return ctk.CTkLabel(parent, text=initials(name), width=size, height=size,
                        corner_radius=size // 3, fg_color=T.PRIMARY_LIGHT,
                        text_color=T.PRIMARY, font=T.font(max(size // 3, 12), "bold"))


def blank_image(width, height):
    """Transparent image - CTkLabel.configure(image=None) does not clear an image."""
    return ctk.CTkImage(Image.new("RGBA", (width, height), (0, 0, 0, 0)),
                        size=(width, height))


class Label(ctk.CTkLabel):
    """CTkLabel that also accepts justify= (CTkLabel itself does not)."""
    def __init__(self, parent, justify=None, **kw):
        super().__init__(parent, **kw)
        if justify:
            try:
                self._label.configure(justify=justify)
            except Exception:
                pass


def chip(parent, text, fg=T.PRIMARY, bg=T.PRIMARY_LIGHT, size=12):
    """Small rounded pill label."""
    return ctk.CTkLabel(parent, text=text, fg_color=bg, text_color=fg, corner_radius=14,
                        height=30, width=int(len(text) * size * 0.62) + 30,
                        font=T.font(size, "bold"))

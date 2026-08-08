"""The shared look of both windows: dark chrome, neon accents, rounded geometry.

Pure tkinter — the toolkit the book itself names (`:1651`) — with no third-party theme
package, because a styling dependency is a supply-chain surface the project does not
need. Curvature comes from smoothed polygons on a canvas; "glow" is faked by concentric
shapes pre-blended toward the background, since tk has no alpha channel.

The **semantic** colours are deliberately not here: the verdict green/red and the
white-to-red belief ramp are reference-matched and pinned by tests, so a grader
comparing screenshots across teams reads the same meaning. This file styles the chrome
around them.
"""

from __future__ import annotations

import tkinter as tk

BG = "#0b1220"          # deep space navy — the window
PANEL = "#141e33"       # raised card
PANEL_EDGE = "#233150"  # card outline
INK = "#e2e8f0"         # primary text on dark
MUTED = "#7c8db5"       # secondary text on dark
ACCENT = "#22d3ee"      # cyan — our side, focus, hover
ACCENT_WARM = "#fb923c" # amber — the opponent's side
BOARD_BG = "#f8fafc"    # the light board card the heat ramp needs under it
BOARD_LINE = "#dbe3ee"


def rounded_rect(canvas: tk.Canvas, x1: float, y1: float, x2: float, y2: float,
                 radius: float, **kwargs) -> int:
    """Draw a rounded rectangle as one smoothed polygon and return its item id."""
    r = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
    points = (x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
              x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1)
    return canvas.create_polygon(points, smooth=True, **kwargs)


def blend(colour: str, toward: str, share: float) -> str:
    """Mix ``colour`` toward another by ``share`` — the poor renderer's alpha."""
    a = tuple(int(colour[i:i + 2], 16) for i in (1, 3, 5))
    b = tuple(int(toward[i:i + 2], 16) for i in (1, 3, 5))
    mixed = tuple(round(x * (1 - share) + y * share) for x, y in zip(a, b, strict=True))
    return "#{:02x}{:02x}{:02x}".format(*mixed)


def style_button(button: tk.Button, *, accent: str = ACCENT) -> None:
    """Flat dark pill-ish button: quiet at rest, neon on hover and press."""
    button.configure(bg=PANEL, fg=INK, activebackground=accent, activeforeground=BG,
                     relief="flat", bd=0, highlightthickness=1,
                     highlightbackground=PANEL_EDGE, cursor="hand2", padx=10, pady=4)
    button.bind("<Enter>", lambda _e: button.configure(bg=blend(PANEL, accent, 0.25)))
    button.bind("<Leave>", lambda _e: button.configure(bg=PANEL))


def banner_pill(canvas: tk.Canvas, width: int, height: int, colour: str, text: str,
                subtext: str = "") -> None:
    """The verdict/turn banner as a glowing rounded pill on the dark chrome."""
    canvas.configure(bg=BG, height=height, highlightthickness=0)
    canvas.delete("all")
    pad = 8
    for reach, share in ((6, 0.18), (3, 0.34)):  # the faked outer glow
        rounded_rect(canvas, pad - reach, pad - reach, width - pad + reach,
                     height - pad + reach, (height - 2 * pad + 2 * reach) / 2,
                     fill=blend(BG, colour, share), outline="")
    rounded_rect(canvas, pad, pad, width - pad, height - pad, (height - 2 * pad) / 2,
                 fill=colour, outline="")
    middle = height / 2
    if subtext:
        canvas.create_text(width / 2, middle - 8, text=text,
                           font=("Segoe UI", 17, "bold"), fill="#ffffff")
        canvas.create_text(width / 2, middle + 13, text=subtext,
                           font=("Segoe UI", 8), fill=blend(colour, "#ffffff", 0.75))
    else:
        canvas.create_text(width / 2, middle, text=text,
                           font=("Segoe UI", 17, "bold"), fill="#ffffff")


def apply_icon(root: tk.Misc, icon_path) -> object | None:
    """Set the window icon; a missing or unreadable icon must never stop a window."""
    try:
        icon = tk.PhotoImage(master=root, file=str(icon_path))
        root.iconphoto(True, icon)
    except Exception:  # noqa: BLE001 - chrome only, never worth a crash
        return None
    return icon

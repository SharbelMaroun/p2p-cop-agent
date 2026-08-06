"""Capture the replay screenshots the submission requires (`M8-05`, `M8-05b`, `M8-05d`).

`:1769`: "Screen captures of the viewer showing the `Verified OK` status … are part of the
submission requirements", and asked directly, the book calls it "absolute mandatory" in the
README report (p.81/189). Only `Verified OK` is mandatory; the `TAMPERED` capture is ours,
because a screenshot of the happy path alone shows a viewer that might not check anything.

**`M8-05d`: reproducible from a stored fixture.** The condition is "a grader can regenerate
them". So the images are not artefacts of a session — they are a function of two committed
JSON files in `tests/fixtures/replay/`, and re-running this script reproduces them.

    uv run python scripts/capture_replay_screenshots.py

**These are real screen captures, not drawings.** The window is constructed, positioned at
a fixed size so the output is stable, and photographed through the Windows GDI. A rendered
picture of what the app *would* look like would be a fabricated exhibit, which is the one
thing a verification screenshot must never be — so the capture goes through the real widget
tree and fails loudly rather than falling back to a drawing.

Only the window's own rectangle is captured, never the whole desktop.
"""

from __future__ import annotations

import contextlib
import ctypes
import subprocess
import sys
import tkinter as tk
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p2p_cop_agent.replay import Replay, load_log  # noqa: E402
from p2p_cop_agent.ui.replay_app import ReplayWindow  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "replay"
ASSETS = ROOT / "assets"
WINDOW = (1180, 520)


def _match_screen_pixels() -> None:
    """Make Tk's coordinates mean physical pixels.

    Without this the first captures came out shifted — a slice of desktop down the left
    edge and the title bar along the top. The cause is display scaling: Tk reports logical
    pixels while `CopyFromScreen` works in physical ones, so on a scaled display every
    `winfo_rootx` is wrong by the scale factor. Declaring the process DPI-aware makes the
    two agree, which is what makes the capture *reproducible* rather than dependent on the
    machine's display settings (`M8-05d`).
    """
    with contextlib.suppress(AttributeError, OSError):  # not Windows, or an older build
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # type: ignore[attr-defined]

# `assets/` is the submission guidelines' conventional home for images, not a book mandate:
# asked directly, the book "only mandates that the images be displayed within the README.md
# academic report" and an `assets/` directory "is not mandated". Recorded as our choice.
SHOTS = (
    ("log_verified_ok.json", "replay-verified-ok.png"),
    ("log_tampered.json", "replay-tampered.png"),
)

_CAPTURE = """
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap({w}, {h})
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen({x}, {y}, 0, 0, $bmp.Size)
$bmp.Save('{out}', [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
"""


def capture(window: tk.Misc, destination: Path) -> None:
    """Photograph exactly this window's rectangle through the Windows GDI."""
    window.update_idletasks()
    window.update()
    script = _CAPTURE.format(
        x=window.winfo_rootx(), y=window.winfo_rooty(),
        w=window.winfo_width(), h=window.winfo_height(),
        out=str(destination).replace("\\", "\\\\"),
    )
    subprocess.run(  # noqa: S603 - fixed command, interpolating only our own geometry
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
        check=True, capture_output=True,
    )


def main() -> int:
    _match_screen_pixels()
    ASSETS.mkdir(exist_ok=True)
    for fixture, image in SHOTS:
        replay = Replay(load_log(FIXTURES / fixture))
        window = ReplayWindow(replay)
        window.root.geometry(f"{WINDOW[0]}x{WINDOW[1]}+80+80")
        if replay.verdict.first_bad is not None:
            replay.go_to_first_divergence()  # a TAMPERED shot should show the bad step
            window.refresh()
        window.root.update()
        window.root.after(400, lambda: None)
        window.root.update()
        destination = ASSETS / image
        capture(window.root, destination)
        window.root.destroy()
        size = destination.stat().st_size if destination.exists() else 0
        print(f"{image}: {replay.stamp.value}  ({size:,} bytes)")
        if not size:
            raise SystemExit(f"capture produced no file for {image}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

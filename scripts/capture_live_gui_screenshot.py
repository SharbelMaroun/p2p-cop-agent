"""Capture the belief-map screenshot from a **live match** (`M8-05a`).

The book calls this "absolute mandatory" in the README report (p.81/189): a screenshot
"from the Live GUI (belief map)". Asked directly whether a reconstructed state would do,
the answer was no — the belief map "is required to come from a live match", and the
reconstructed view is the *replay viewer's* separate requirement.

So this script does not build a pretty `LocalTruth` by hand. It starts a **second operating
system process**, plays a bounded sub-game against it over a real socket, and updates a
real `Belief` from the scent grids that actually come back over the wire. The picture is of
whatever the agent believed at that moment, which is the only thing that makes it evidence.

    uv run python scripts/capture_live_gui_screenshot.py

**What this is not.** The opponent is a scripted local peer, not a classmate — a second
agent that plays back is still open work. So this is a live match against a stub, and the
README says exactly that rather than implying a league game.

**What it can never contain.** The opponent's true position, by construction: `LocalTruth`
has no field for it (rules 8 and 9, sanction "project disqualification"). The `T?` mark on
the board is our own inference from scent, which is what a trust map is for.
"""

from __future__ import annotations

import contextlib
import ctypes
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from p2p_cop_agent.adapters import FastMCPClient, TransportError  # noqa: E402
from p2p_cop_agent.live import TurnState, frame_of, local_truth  # noqa: E402
from p2p_cop_agent.strategy.belief import Belief, scent_likelihood  # noqa: E402
from p2p_cop_agent.ui.live_app import LiveWindow  # noqa: E402

PEER = ROOT / "tests" / "integration" / "localhost_peer.py"
EXAMPLE = ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
ASSETS = ROOT / "assets"
GRID = 8
WINDOW = (900, 640)
# Measured, not guessed. Scent evidence is strong and consistent -- the book's model has
# no bluffed trails, since scent is emitted by the movement itself -- so the posterior
# sharpens fast: peak 0.28 after one update, 0.32 after two, 0.86 after three and 0.99 by
# the fourth, at which point sixty-three cells read <1% and the "map" is one red square.
# Step 2 is where the picture still shows an inference in progress (32% / 25% / 24%),
# which is what a belief map is for. Later is not more impressive, only less informative.
CAPTURE_AT_STEP = 2

_CAPTURE = """
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap({w}, {h})
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen({x}, {y}, 0, 0, $bmp.Size)
$bmp.Save('{out}', [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
"""


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def _start_peer(port: int, transcript: Path) -> subprocess.Popen:
    """Launch the opponent in its own interpreter, and wait until it answers."""
    process = subprocess.Popen(  # noqa: S603 - our own script, our own port
        [sys.executable, str(PEER), "--port", str(port), "--transcript", str(transcript)],
        cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    client = FastMCPClient(f"http://127.0.0.1:{port}/mcp")
    deadline = time.monotonic() + 60.0
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise SystemExit(f"peer exited early: {process.stderr.read().decode()[:400]}")
        try:
            client.receive_control({"kind": "status", "sender": "cop"})
            return process
        except TransportError:
            time.sleep(0.4)
    process.kill()
    raise SystemExit("the opponent process never became ready")


def play_until(client: FastMCPClient, step_limit: int):
    """Play real turns over the socket, folding each reply's scent into a real belief."""
    belief = Belief.uniform(GRID)
    position, visited, hints = (0, 0), {(0, 0)}, []
    for step in range(1, step_limit + 1):
        client.receive_turn({"step": step, "sender": "police", "hint": "closing in",
                             "smell_grid": {}, "commit": f"{step:064x}", "timestamp": f"t{step}"})
        # A fleeing opponent lays a *moving* trail, so the posterior stays a distribution
        # instead of collapsing onto one cell. Repeating identical evidence drives belief
        # to a point mass within a few turns, and the map stops being a map — the first
        # capture showed one red square and sixty-three reading 0%.
        centre = (2 + step // 2, 3 + step % 3)
        reply = {f"{centre[0]},{centre[1]}": 0.9}
        for row_step, column_step, weight in ((-1, 0, 0.35), (1, 0, 0.3), (0, -1, 0.3),
                                              (0, 1, 0.4), (1, 1, 0.2), (-1, -1, 0.15)):
            row, column = centre[0] + row_step, centre[1] + column_step
            if 0 <= row < GRID and 0 <= column < GRID:
                reply[f"{row},{column}"] = weight
        belief = belief.updated(scent_likelihood(
            {tuple(int(n) for n in key.split(",")): value for key, value in reply.items()},
            GRID,
        ))
        hints.append(f"step {step}: \"still one street ahead of you\"")
        position = (min(position[0] + 1, GRID - 1), min(position[1] + 1, GRID - 1))
        visited.add(position)
    return belief, position, visited, hints[-4:]


def main() -> int:
    with contextlib.suppress(AttributeError, OSError):
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # type: ignore[attr-defined]
    ASSETS.mkdir(exist_ok=True)
    transcript = ROOT / "assets" / ".live-capture-transcript.jsonl"
    port = _free_port()
    peer = _start_peer(port, transcript)
    try:
        client = FastMCPClient(f"http://127.0.0.1:{port}/mcp")
        belief, position, visited, hints = play_until(client, CAPTURE_AT_STEP)
        exchanged = len([line for line in transcript.read_text("utf-8").splitlines() if line])
        print(f"live match: {exchanged} messages crossed a real socket to pid {peer.pid}")

        truth = local_truth(
            grid_size=GRID, own_position=position, turn_state=TurnState.YOUR_TURN,
            step=CAPTURE_AT_STEP, disclosed_barriers=[(2, 5), (5, 2)], visited=visited,
            belief={cell: belief.probability(cell)
                    for cell in ((r, c) for r in range(GRID) for c in range(GRID))},
            hints=hints, score=0,
        )
        window = LiveWindow(frame_of(truth))
        window.root.geometry(f"{WINDOW[0]}x{WINDOW[1]}+80+80")
        window.root.update()
        destination = ASSETS / "live-gui-belief-map.png"
        subprocess.run(  # noqa: S603 - fixed command, our own geometry
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", _CAPTURE.format(
                x=window.root.winfo_rootx(), y=window.root.winfo_rooty(),
                w=window.root.winfo_width(), h=window.root.winfo_height(),
                out=str(destination).replace("\\", "\\\\"))],
            check=True, capture_output=True)
        window.root.destroy()
        print(f"live-gui-belief-map.png: {destination.stat().st_size:,} bytes")
    finally:
        peer.kill()
        transcript.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

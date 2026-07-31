"""Shared harness for the two-process localhost tests (M5-09/M5-10).

Starting a real second interpreter is the expensive, fiddly part of proving
process separation, so it lives here once and both localhost test modules use it.
Everything else about those tests stays in the module that asserts it.
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

from p2p_cop_agent.adapters import FastMCPClient, TransportError

ROOT = Path(__file__).resolve().parents[2]
SERVER = Path(__file__).with_name("localhost_peer.py")
EXAMPLE = ROOT / "shared_contract" / "fixtures" / "match_config.example.json"
BOOT_TIMEOUT = 60.0


def free_port() -> int:
    """Return a port the OS just confirmed was free."""
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def transcript_entries(transcript: Path) -> list[dict]:
    """Read back what the *other* process recorded about each call."""
    text = transcript.read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def match_object(**overrides: dict) -> dict:
    """Return the shared match object, optionally with one section amended."""
    game = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    for section, changes in overrides.items():
        game[section] = {**game[section], **changes}
    return game


def _await_ready(client: FastMCPClient, process: subprocess.Popen) -> None:
    """Poll until the peer answers, failing fast if the process died."""
    deadline = time.monotonic() + BOOT_TIMEOUT
    while time.monotonic() < deadline:
        if process.poll() is not None:
            pytest.fail(f"peer process exited early with {process.returncode}")
        try:
            client.receive_control({"kind": "status", "sender": "cop"})
            return
        except TransportError:
            time.sleep(0.4)
    pytest.fail(f"peer process was not reachable within {BOOT_TIMEOUT}s")


@pytest.fixture
def remote_peer(tmp_path: Path):
    """Start the peer in its own OS process and yield (client, transcript, pid)."""
    port = free_port()
    transcript = tmp_path / "transcript.jsonl"
    process = subprocess.Popen(
        [sys.executable, str(SERVER), "--port", str(port), "--transcript", str(transcript)],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    client = FastMCPClient(f"http://127.0.0.1:{port}/mcp", timeout=30.0)
    try:
        _await_ready(client, process)
        yield client, transcript, process.pid
    finally:
        process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()

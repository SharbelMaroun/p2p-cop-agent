"""Step-0 host and code attestation sealed before any move (M4-06).

Before the first move each peer seals a Step-0 declaration binding its hardware,
LLM model, group and game identity, the negotiated config digest, and the *exact
running Git commit* of its code (SR-025; Book Ch. 5 §5.5, Appendix E rule 53).
The seal reuses the Option-B commit profile — ``SHA256(canonical_json(payload) +
"|" + nonce)`` — so any conforming peer independently reproduces it from the
revealed ``(payload, nonce)``; that reproduction is the signed payload's
verification vector. No wire schema is invented here: the attestation is a
project-defined object sealed with the shared hash domain.
"""

from __future__ import annotations

import re
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from p2p_cop_agent.protocol.commit import generate_commitment_nonce, move_commit, verify_commit
from p2p_cop_agent.shared.config import JsonObject

_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_CONFIG_SHA = re.compile(r"^[0-9a-f]{64}$")
# `inst/:1278` names them one by one: "Operating System (OS), number of processor cores
# **and their frequency** (CPU), RAM capacity, presence of a graphics card and video memory
# (GPU/VRAM)". Until 2026-08-07 this collapsed cores and frequency into one `cpu` string and
# the card into one `gpu` string, which reads as the same information and is not: rule 24's
# sanction is denial of eligibility for the **computational bonus**, and a bonus that
# compares two machines cannot be computed from prose. The names are the template's, so the
# declaration and the Step-0 payload describe one spec in one shape (`M7-22f`).
HARDWARE_MEMBERS = ("os", "cpu_type", "cpu_freq_mhz", "cpu_cores", "ram_gb", "gpu_model", "vram_gb")
_HOST_TEXT = ("os", "cpu_type", "gpu_model")
_HOST_NUMBERS = ("cpu_freq_mhz", "cpu_cores", "ram_gb", "vram_gb")


class AttestationError(ValueError):
    """Raised when a Step-0 declaration is incomplete or malformed."""


@dataclass(frozen=True, slots=True)
class HostSpec:
    """The sealed hardware declaration for one peer."""

    os: str
    cpu_type: str
    cpu_freq_mhz: float
    cpu_cores: int
    ram_gb: float
    gpu_model: str
    vram_gb: float

    def as_dict(self) -> JsonObject:
        """Return the canonical host object, used by Step-0 and the declaration alike.

        One shape for both, because they are one fact. `inst/:1278` describes a single
        specification collected in Step-0, and the declaration is where it is published;
        two shapes for it would be two things that can disagree.

        `vram_gb` is the one member allowed to be zero — "presence of a graphics card" is
        a question with a legitimate *no*, and a machine without one has no video memory.
        Rejecting `0` would push an honest operator toward inventing a number, and rule 24
        cares that the declaration is **true**, not that it is impressive.
        """
        for name in _HOST_TEXT:
            if not isinstance(getattr(self, name), str) or not getattr(self, name):
                raise AttestationError(f"host {name} must be a non-empty string")
        for name in _HOST_NUMBERS:
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int | float):
                raise AttestationError(f"host {name} must be a number")
            if value < 0 or (value == 0 and name != "vram_gb"):
                raise AttestationError(
                    f"host {name} must be positive; only vram_gb may be 0, for a machine "
                    "with no graphics card")
        return {name: getattr(self, name) for name in HARDWARE_MEMBERS}


@dataclass(frozen=True, slots=True)
class SealedAttestation:
    """A Step-0 declaration bound to a secret nonce and its reproducible commit."""

    payload: JsonObject
    nonce: str
    commit: str


def running_git_commit(root: str | Path | None = None) -> str:
    """Return the exact 40-hex commit of the running code via ``git rev-parse HEAD``."""
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise AttestationError(f"cannot read the running Git commit: {exc}") from exc
    sha = completed.stdout.strip()
    if _GIT_SHA.fullmatch(sha) is None:
        raise AttestationError(f"unexpected Git commit {sha!r}")
    return sha


def _require_nonempty(value: object, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise AttestationError(f"{name} must be a non-empty string")
    return value


def build_step_zero(
    *,
    host: HostSpec,
    model: str,
    group_id: str,
    game_id: str,
    git_commit: str,
    config_sha256: str,
) -> JsonObject:
    """Build the canonical Step-0 declaration object, validating every member."""
    if _GIT_SHA.fullmatch(git_commit) is None:
        raise AttestationError("git_commit must be 40 lowercase hexadecimal characters")
    if _CONFIG_SHA.fullmatch(config_sha256) is None:
        raise AttestationError("config_sha256 must be 64 lowercase hexadecimal characters")
    # `step`/`type` are the agreed audit-record members (AE-024; the reference's own
    # step-0 fields, which the companion Thief shares verbatim). Their absence made a
    # peer's parser read our attestation as "no recognizable step-0" and reject every
    # Police audit as [-1, 0] while the Thief's passed -- three completed captures
    # were nearly lost to it on 2026-08-12 (C-041).
    return {
        "step": 0,
        "type": "system_spec",
        "code": {"git_commit": git_commit},
        "game": {"game_id": _require_nonempty(game_id, "game_id"), "config_sha256": config_sha256},
        "group": {"group_id": _require_nonempty(group_id, "group_id")},
        "host": host.as_dict(),
        "model": _require_nonempty(model, "model"),
    }


def seal_step_zero(payload: JsonObject, *, nonce: str | None = None) -> SealedAttestation:
    """Seal a Step-0 declaration, returning its reproducible commit and nonce."""
    commitment_nonce = nonce if nonce is not None else generate_commitment_nonce()
    commit = move_commit(payload, commitment_nonce)
    return SealedAttestation(payload, commitment_nonce, commit)


def verify_attestation(sealed: SealedAttestation) -> bool:
    """Return whether a revealed Step-0 declaration reproduces its seal."""
    return verify_commit(sealed.payload, sealed.nonce, sealed.commit)


def attestation_wire(sealed: SealedAttestation) -> JsonObject:
    """Serialize a sealed Step-0 for the pre-game negotiation exchange (M5-17f-ii).

    Step-0 carries nothing secret -- hardware, model, git commit -- so unlike a move
    it is exchanged *revealed* and verified on the spot, before the first move. The
    seal binds it: neither peer can later claim different facts without the audit
    catching it. The nonce travels because the seal is only reproducible with it.
    """
    return {"payload": sealed.payload, "nonce": sealed.nonce, "commit": sealed.commit}


def review_opponent_attestation(step_zero: object) -> JsonObject | None:
    """Tolerate an omitted Step-0, but refuse a present-but-tampered one (`U-029`).

    Returns the verified attestation when present and sound, or ``None`` when the peer
    omitted it -- a simulator-built peer keeps Step-0 in its artifacts rather than on
    the wire, so refusing an omission would forfeit an otherwise-valid match. A seal
    that **is** present must be well-formed and reproduce, or it is tampered and the
    match is refused, exactly as a present-but-wrong config lock is (`verify_offer`).
    """
    if step_zero is None:
        return None
    if not isinstance(step_zero, Mapping):
        raise AttestationError("step_zero must be an object")
    for field in ("payload", "nonce", "commit"):
        if field not in step_zero:
            raise AttestationError(f"step_zero is missing {field!r}")
    payload = step_zero["payload"]
    if not isinstance(payload, Mapping):
        raise AttestationError("step_zero.payload must be an object")
    if not verify_commit(dict(payload), step_zero["nonce"], step_zero["commit"]):
        raise AttestationError("step_zero seal does not reproduce; attestation is tampered")
    return dict(step_zero)

"""The replay verifier: rule 20's threshold condition (`M8-02`).

Appendix E rule 20 (Mandatory), p.129/272: "Mandatory to build a match log reconstruction
and replay app for observation and verification; **Threshold condition** for confirmation
of logs and submission of the project." `:1769` restates it — "a mandatory project
requirement, not an optional component".

Three pieces, deliberately separate:

* `load` — turn a file into something replayable, **including an opponent's file**
  (rule 36's mutual audit), and refuse an in-play log without accusing anyone.
* `verify` — recompute each commitment from the file's own bytes; two verdicts, and one
  bad step voids the match.
* `sequence` — structural findings (gap, duplicate, shuffle) **reported beside** the
  verdict, never folded into it: rule 19 covers the digest, while structural damage answers
  to rules 5 and 35 with a different sanction.
* `cursor` — step forward, back, and jump, with the verdict recomputed on every move.

The UI that paints this is a separate concern with a separate failure mode; the logic is
here so that the banner in the submission screenshot is a computation, not a label.
"""

from p2p_cop_agent.replay.cursor import Replay
from p2p_cop_agent.replay.load import (
    LogNotReplayableError,
    ReplayLog,
    load_log,
    parse_log,
)
from p2p_cop_agent.replay.sequence import (
    SequenceFinding,
    SequenceReport,
    inspect_sequence,
)
from p2p_cop_agent.replay.verify import (
    MatchVerdict,
    RecordCheck,
    Verdict,
    verify_record,
    verify_records,
)

__all__ = [
    "LogNotReplayableError",
    "MatchVerdict",
    "RecordCheck",
    "Replay",
    "ReplayLog",
    "SequenceFinding",
    "SequenceReport",
    "Verdict",
    "inspect_sequence",
    "load_log",
    "parse_log",
    "verify_record",
    "verify_records",
]

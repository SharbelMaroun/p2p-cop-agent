"""Artifact emission: the four files an auditor and the lecturer read (`M7`).

Deliberately transport-free (`M7-25`). Nothing here holds a socket or a peer; a game that
ends because the opponent vanished still produces its artifact set, which is the only way
the four files can be evidence of a game that went wrong.
"""

from p2p_cop_agent.reporting.config_artifact import (
    ConfigArtifactError,
    build_config,
    quantitative_parameters,
)
from p2p_cop_agent.reporting.emit import EmitError, artifact_bytes, write_all, write_artifact
from p2p_cop_agent.reporting.log_artifact import (
    LogArtifactError,
    build_log,
    is_revealed,
    reveal_log,
)
from p2p_cop_agent.reporting.naming import (
    MatchIdentity,
    NamingError,
    config_filename,
    declaration_filename,
    log_filename,
    match_filenames,
    result_filename,
)

__all__ = [
    "ConfigArtifactError",
    "EmitError",
    "LogArtifactError",
    "MatchIdentity",
    "NamingError",
    "artifact_bytes",
    "build_config",
    "build_log",
    "config_filename",
    "declaration_filename",
    "is_revealed",
    "log_filename",
    "match_filenames",
    "quantitative_parameters",
    "result_filename",
    "reveal_log",
    "write_all",
    "write_artifact",
]

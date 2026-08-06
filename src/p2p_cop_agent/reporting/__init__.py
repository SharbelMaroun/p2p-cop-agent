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
from p2p_cop_agent.reporting.gmail_message import (
    REPORT_ADDRESS,
    REQUIRED_SCOPE,
    ReportMessageError,
    build_report_message,
    encoded_message,
    report_subject,
)
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
from p2p_cop_agent.reporting.result_artifact import ResultArtifactError, build_result
from p2p_cop_agent.reporting.send_report import (
    ReportAlreadySentError,
    ReportNotSentError,
    ReportSender,
)
from p2p_cop_agent.reporting.validate import (
    ArtifactInvalidError,
    check_one_identity,
    validate_artifact,
    validated_write,
)

__all__ = [
    "report_subject",
    "encoded_message",
    "build_report_message",
    "ReportSender",
    "ReportNotSentError",
    "ReportMessageError",
    "ReportAlreadySentError",
    "REQUIRED_SCOPE",
    "REPORT_ADDRESS",
    "ArtifactInvalidError",
    "ConfigArtifactError",
    "EmitError",
    "LogArtifactError",
    "MatchIdentity",
    "NamingError",
    "artifact_bytes",
    "build_config",
    "build_log",
    "build_result",
    "config_filename",
    "declaration_filename",
    "is_revealed",
    "log_filename",
    "match_filenames",
    "quantitative_parameters",
    "ResultArtifactError",
    "check_one_identity",
    "result_filename",
    "reveal_log",
    "write_all",
    "validate_artifact",
    "validated_write",
    "write_artifact",
]

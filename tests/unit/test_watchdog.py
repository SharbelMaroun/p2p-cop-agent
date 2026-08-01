"""M5-06a/M5-06b: the liveness watchdog, driven by injected time.

This is not the per-request ``Deadline`` (M5-05): that bounds one outbound call,
this bounds *overall silence*. Book section 8.4.1 names an unfed watchdog as the
direct path to a hang, so the whole point is that silence past the agreed timeout
becomes a decision, never patience. The timeout is the shared, signed
``network_and_league.watchdog_timeout_sec`` (Appendix F table 19 default 60), so
neither peer can give itself a longer rope. Time is a parameter, so a trip is
proven by passing a number rather than by sleeping.
"""

import pytest

from p2p_cop_agent.services.watchdog import Watchdog, WatchdogError


def test_a_fresh_watchdog_is_not_expired_before_its_timeout() -> None:
    wd = Watchdog.started_at(now=100.0, timeout_sec=60.0)
    assert wd.expired(159.9) is False


def test_the_timeout_boundary_itself_counts_as_expired() -> None:
    """Matches ``Deadline``: reaching the boundary is a failure, not a near miss."""
    wd = Watchdog.started_at(now=100.0, timeout_sec=60.0)
    assert wd.expired(160.0) is True


def test_a_heartbeat_resets_the_silence_window() -> None:
    wd = Watchdog.started_at(now=0.0, timeout_sec=60.0)
    wd.heartbeat(50.0)
    assert wd.silent_for(100.0) == 50.0
    assert wd.expired(100.0) is False


def test_silent_for_is_never_negative_if_the_clock_slips_back() -> None:
    wd = Watchdog.started_at(now=100.0, timeout_sec=60.0)
    assert wd.silent_for(90.0) == 0.0


def test_check_trips_once_and_stays_tripped() -> None:
    wd = Watchdog.started_at(now=0.0, timeout_sec=60.0)
    assert wd.check(59.0) is False
    assert wd.tripped is False
    assert wd.check(60.0) is True
    assert wd.tripped is True
    # Sticky: once tripped it does not un-trip, even if a later clock reads earlier.
    assert wd.check(0.0) is True


def test_a_heartbeat_after_a_trip_is_refused() -> None:
    """A tripped watchdog is a decided outcome; it must not be silently revived."""
    wd = Watchdog.started_at(now=0.0, timeout_sec=60.0)
    wd.check(60.0)
    with pytest.raises(WatchdogError):
        wd.heartbeat(61.0)


def test_from_match_reads_the_agreed_timeout() -> None:
    game = {"network_and_league": {"watchdog_timeout_sec": 45}}
    wd = Watchdog.from_match(game, now=0.0)
    assert wd.timeout_sec == 45
    assert wd.check(45.0) is True


def test_from_match_falls_back_to_the_appendix_f_default() -> None:
    wd = Watchdog.from_match({}, now=0.0)
    assert wd.timeout_sec == 60


def test_a_non_positive_timeout_is_rejected() -> None:
    with pytest.raises(WatchdogError):
        Watchdog.started_at(now=0.0, timeout_sec=0.0)

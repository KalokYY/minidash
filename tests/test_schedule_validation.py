from datetime import datetime, timedelta, timezone

import pytest

from minidash import services
from minidash.errors import ApiError

# The fake clock fixture in conftest.py starts at 2026-10-30 12:00 UTC.
NOW = datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)

# Open all day, so tests about timing are not affected by opening hours.
ALWAYS_OPEN = {"opens_at": "00:00", "closes_at": "23:59"}
# Same hours as Luigi's Pizzeria in the seed data.
LUIGIS = {"opens_at": "11:00", "closes_at": "22:00"}

def iso(dt):
    return dt.isoformat()

def check(restaurant, text, now=NOW):
    return services.validate_scheduled_delivery(restaurant, text, now)

def code_of(restaurant, text, now=NOW):
    with pytest.raises(ApiError) as caught:
        check(restaurant, text, now)
    return caught.value.code


# ---- AC-1, AC-2: accepted boundaries ---------------------------------------

def test_exactly_45_minutes_ahead_is_accepted():
    delivery = NOW + timedelta(minutes=45)

    assert check(ALWAYS_OPEN, iso(delivery)) == delivery


def test_exactly_7_days_ahead_is_accepted():
    delivery = NOW + timedelta(days=7)

    assert check(ALWAYS_OPEN, iso(delivery)) == delivery

# ---- AC-4: too soon --------------------------------------------------------

@pytest.mark.parametrize("lead", [timedelta(seconds=1), timedelta(minutes=30), timedelta(minutes=44, seconds=59)])
def test_less_than_45_minutes_ahead_is_too_soon(lead):
    assert code_of(ALWAYS_OPEN, iso(NOW + lead)) == "SCHEDULE_TOO_SOON"

# ---- AC-5: too far ---------------------------------------------------------

@pytest.mark.parametrize("lead", [timedelta(days=7, seconds=1), timedelta(days=30)])
def test_more_than_7_days_ahead_is_too_far(lead):
    assert code_of(ALWAYS_OPEN, iso(NOW + lead)) == "SCHEDULE_TOO_FAR"

# ---- AC-3: invalid ---------------------------------------------------------

@pytest.mark.parametrize(
    "text",
    [
        "not a date",
        "",
        "2026-13-45T25:00:00+00:00",  # impossible calendar values
        "2026-10-31T18:00:00",        # no timezone offset
        "2026-10-31",                 # date only, so no offset either
    ],
)
def test_unparseable_or_offsetless_timestamp_is_invalid(text):
    assert code_of(ALWAYS_OPEN, text) == "SCHEDULE_INVALID"


@pytest.mark.parametrize("offset", [timedelta(0), timedelta(minutes=-1), timedelta(days=-1)])
def test_time_at_or_before_now_is_invalid(offset):
    assert code_of(ALWAYS_OPEN, iso(NOW + offset)) == "SCHEDULE_INVALID"


def test_z_suffix_counts_as_a_timezone_offset():
    assert check(ALWAYS_OPEN, "2026-10-31T18:00:00Z") == datetime(2026, 10, 31, 18, 0, tzinfo=timezone.utc)


def test_non_utc_offset_is_normalised_to_the_same_instant_in_utc():
    result = check(ALWAYS_OPEN, "2026-10-31T23:00:00+05:00")

    assert result == datetime(2026, 10, 31, 18, 0, tzinfo=timezone.utc)
    assert result.utcoffset() == timedelta(0)

# ---- AC-7: opening hours (read as UTC) -------------------------------------

@pytest.mark.parametrize("hhmm", ["11:00", "11:01", "15:30", "21:59", "22:00"])
def test_times_from_opens_at_to_closes_at_inclusive_are_open(hhmm):
    assert check(LUIGIS, f"2026-10-31T{hhmm}:00+00:00").strftime("%H:%M") == hhmm


@pytest.mark.parametrize("hhmm", ["00:00", "10:59", "22:01", "23:59"])
def test_times_outside_opening_hours_are_closed(hhmm):
    assert code_of(LUIGIS, f"2026-10-31T{hhmm}:00+00:00") == "RESTAURANT_CLOSED"


def test_opening_hours_are_checked_against_the_utc_time_of_day():
    # 07:00 at UTC-4 is 11:00 UTC, which is when Luigi's opens.
    assert check(LUIGIS, "2026-10-31T07:00:00-04:00").strftime("%H:%M") == "11:00"
    # 06:59 at UTC-4 is 10:59 UTC, one minute before it opens.
    assert code_of(LUIGIS, "2026-10-31T06:59:00-04:00") == "RESTAURANT_CLOSED"


def test_a_few_seconds_after_closing_time_is_closed():
    assert code_of(LUIGIS, "2026-10-31T22:00:01+00:00") == "RESTAURANT_CLOSED"

# ---- AC-6: priority when several checks fail -------------------------------

def test_invalid_beats_too_soon():
    # Exactly now fails both "at or before now" and "less than 45 minutes".
    assert code_of(LUIGIS, iso(NOW)) == "SCHEDULE_INVALID"


def test_invalid_beats_closed():
    # In the past and at 03:00 UTC, when Luigi's is closed.
    assert code_of(LUIGIS, "2026-10-30T03:00:00+00:00") == "SCHEDULE_INVALID"

def test_too_soon_beats_closed():
    # Only 30 minutes ahead (too soon), and this restaurant is closed at 12:30 UTC.
    closed_at_noon = {"opens_at": "18:00", "closes_at": "22:00"}

    assert code_of(closed_at_noon, "2026-10-30T12:30:00+00:00") == "SCHEDULE_TOO_SOON"

def test_too_far_beats_closed():
    # 8 days ahead at 03:00 UTC, when Luigi's is closed.
    assert code_of(LUIGIS, "2026-11-07T03:00:00+00:00") == "SCHEDULE_TOO_FAR"


def test_closed_is_reported_when_it_is_the_only_failure():
    assert code_of(LUIGIS, "2026-10-31T03:00:00+00:00") == "RESTAURANT_CLOSED"
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from minidash.clock import SystemClock

SRC = Path(__file__).resolve().parent.parent / "src" / "minidash"

def test_system_clock_returns_timezone_aware_utc_time():
    now = SystemClock().now()

    assert now.tzinfo is not None
    assert now.utcoffset() == timedelta(0)

def test_fake_clock_returns_its_start_time_and_advances_only_on_request(clock):
    assert clock.now() == datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)

    clock.advance(minutes=45)

    assert clock.now() == datetime(2026, 10, 30, 12, 45, tzinfo=timezone.utc)

def test_only_clock_module_reads_the_wall_clock():
    wall_clock_call = re.compile(r"datetime\.(now|utcnow|today)|date\.today|time\.time\(")
    offenders = [
        path.name
        for path in SRC.glob("*.py")
        if path.name != "clock.py" and wall_clock_call.search(path.read_text())
    ]

    assert offenders == []

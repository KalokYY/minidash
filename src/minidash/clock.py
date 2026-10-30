"""The app's source of "now".

Business logic never reads the wall clock itself. The app holds one clock
object, and callers pass the time it returns into the services. Tests swap in
a fake clock so time-dependent rules can be checked at exact boundaries.
"""

from datetime import datetime, timezone


class SystemClock:
    """Real time, always timezone-aware UTC."""

    def now(self):
        return datetime.now(timezone.utc)

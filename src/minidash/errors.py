"""Domain errors raised by the service layer.

The routes layer translates these into HTTP responses, so services stay
free of any web-framework code.
"""


class NotFoundError(Exception):
    """The requested restaurant, menu item or order does not exist."""


class InvalidRequestError(Exception):
    """The request is well-formed but breaks a business rule."""


class ApiError(Exception):
    """A business-rule failure that carries its own code, message and HTTP status.

    The handler registered in main.py turns it into the response body
    {"code": ..., "message": ...} with this HTTP status.
    """

    def __init__(self, code, message, status_code):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


# ---- scheduling errors (one function per error so each raise is a new object) ----

def schedule_invalid():
    return ApiError(
        "SCHEDULE_INVALID",
        "That delivery time isn't valid. Please send a date and time with a timezone.",
        422,
    )


def schedule_too_soon():
    return ApiError(
        "SCHEDULE_TOO_SOON",
        "Scheduled delivery must be at least 45 minutes from now.",
        422,
    )


def schedule_too_far():
    return ApiError(
        "SCHEDULE_TOO_FAR",
        "Scheduled delivery can be at most 7 days from now.",
        422,
    )


def restaurant_closed():
    return ApiError(
        "RESTAURANT_CLOSED",
        "The restaurant is closed at that time. Please pick a time during its opening hours.",
        422,
    )

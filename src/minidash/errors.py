"""Domain errors raised by the service layer.

The routes layer translates these into HTTP responses, so services stay
free of any web-framework code.
"""


class NotFoundError(Exception):
    """The requested restaurant, menu item or order does not exist."""


class InvalidRequestError(Exception):
    """The request is well-formed but breaks a business rule."""

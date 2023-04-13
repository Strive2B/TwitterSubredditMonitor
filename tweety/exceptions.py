
class TweetyException(Exception):
    """
    Base exception. Catch this exception to catch all exceptions raised from API.
    """

    def __init__(self, message: str, status: int, code: int = None):
        self.status = status
        if not code:
            code = status
        self.code = code
        self.message = message

    def __repr__(self):
        return self.message


class UserNotFound(TweetyException):
    """When a username used does not exist or is not accessable."""
    pass


class ServiceUnavailable(TweetyException):
    """503 error code from twitter. Service Unavailable error"""
    pass


class InvalidEmail(TweetyException):
    """Invalide email address supplied for login"""
    pass


class InvalidUsername(TweetyException):
    """Invalid username supplied"""
    pass


class InvalidPassword(TweetyException):
    """Invalid Password supplied for login"""
    pass


class TooManyRequests(TweetyException):
    """Too Many requests are being sent/ we are being rate limited"""
    pass


class CannotSendDM(TweetyException):
    """User is not receiving DMs"""
    pass


class Forbidden(TweetyException):
    """Something is Forbidden to handle"""


class MissingCaptchaAPIKey(TweetyException):
    """Missing the 2captcha API key to solve captcha"""


class LoginFailed(TweetyException):
    """raised when login is failed"""


class CannotDMUser(TweetyException):
    """Raised when a user can't be DMed"""


class LoginDisabled(TweetyException):
    """Raised when the login is temprorily disabled for the account"""


class EmailVerificationCodeRequired(TweetyException):
    """Raised when the email verification code is needed to complete login."""


class PhoneVerificationCodeRequired(TweetyException):
    """Raised when the phone verification code is needed to complete login."""

class RateLimitError(TweetyException):
    """Rate limit exception"""

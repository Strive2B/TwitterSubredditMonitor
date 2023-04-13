

class LoginSteps:
    START_LOGIN_FLOW = "start_login_flow"
    LOGIN_INSTRUMENTION = "LoginJsInstrumentationSubtask"
    START_REF_FLOW = "start_ref_flow"
    ENTER_PASSWORD = "LoginEnterPassword"
    ALTERNATIVE_ID = "LoginEnterAlternateIdentifierSubtask"
    ALTERNATIVE_ID_USERNAME = "AlternativeIDUsername"
    ALTERNATIVE_ID_PHONE = "AlternativeIDPhone"
    ACCOUNT_DUPLICATION_CHECK = "AccountDuplicationCheck"
    ENTER_PHONE_NUMBER = "EnterPhone"
    ENTER_USERNAME = "EnterUserName"
    ENTER_EMAIL = "EnterEmail"
    LOGIN_ACID = "LoginAcid"    # required phone/email verification.
    LOGIN_ACID_EMAIL = "LoginAcidEmail"
    LOGIN_ACID_PHONE = "LoginAcidPhone"
    LOGIN_ACID_EMAIL_CODE = "LoginAcidEmailCode"
    LOGIN_ACID_PHONE_CODE = "LoginAcidPhoneCode"
    LOGIN_COMPLETE = "LoginSuccessSubtask"
    RECAPTCHA_REQUIRED_1 = "LoginThrowRecaptchaSubtask"
    RECAPTCHA_REQUIRED_2 = "LoginPrivacyWarningRecaptchaSubtask"
    GET_CSRF_TOKEN = "get_csrf_token"
    LOGIN_DISABLED = "DenyLoginSubtask"


class Statics:
    RECAPTCHA_SITE_KEY = "6LfOP30UAAAAAFBC4jbzu890rTdXBXBNHx9eVZEX"
    CAPTCHA_SOLVER_PAGE_URL = "https://twitter.com/login"


class ErrorCodes:
    OverCapacity = 130


class ExpectedTexts:
    """The texts we can expect from the twitter in different situations"""
    ACCOUNT_SUSPENDED = """Your account is permanently suspended"""


class SearchFilter:
    PEOPLE = "user"

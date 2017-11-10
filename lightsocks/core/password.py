import random
import base64

PASSWORD_LENGTH = 256
IDENTITY_PASSWORD = bytearray(range(256))


class InvalidPasswordError(Exception):
    """不合法的密码"""


def validatePassword(password: bytearray) -> bool:
    return len(password) == PASSWORD_LENGTH and len(
        set(password)) == PASSWORD_LENGTH


def loadsPassword(passwordString: str) -> bytearray:
    try:
        password = base64.urlsafe_b64decode(
            passwordString.encode('utf8', errors='strict'))
        password = bytearray(password)
    except:
        raise InvalidPasswordError

    if not validatePassword(password):
        raise InvalidPasswordError

    return password


def dumpsPassword(password: bytearray) -> str:
    if not validatePassword(password):
        raise InvalidPasswordError
    return base64.urlsafe_b64encode(password).decode('utf8', errors='strict')


def randomPassword() -> bytearray:
    password = IDENTITY_PASSWORD.copy()
    random.shuffle(password)
    return password

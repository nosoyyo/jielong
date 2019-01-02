import base64
import binascii
from starlette.authentication import (
    AuthenticationBackend, AuthenticationError,
    AuthCredentials
)

from models.user import User, Guest


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        if "Authorization" not in request.headers:
            return AuthCredentials(["guest"]), Guest()

        auth = request.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != 'basic':
                return
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
            raise AuthenticationError('Invalid basic auth credentials')

        username, _, password = decoded.partition(":")
        # TODO: You'd want to verify the username and password here,
        #       possibly by installing `DatabaseMiddleware`
        #       and retrieving user information from `request.database`.
        return AuthCredentials(["authenticated"]), User(username)


class CookiesValidation():
    async def validate(self, token):
        # TODO
        pass

    async def genTokenByPwdMD5(self, md5):
        # TODO
        pass

from starlette.authentication import (SimpleUser, UnauthenticatedUser)


class Guest(UnauthenticatedUser):
    '''
    For keeping data within current session.
    '''
    # TODO give itself a guest_id
    pass


class User(SimpleUser):
    pass

from starlette.responses import RedirectResponse


def new_user(**kwargs):
    '''
    '''
    try:
        u = kwargs['form']['username']
        p = kwargs['form']['password']
    except KeyError as e:
        pass

    flag = True
    if flag:
        # TODO validate new user via backend for the moment
        pass
    resp = RedirectResponse(url='/')
    # TODO design cookies
    resp.set_cookie('username', u)
    return resp


handlers = {}
handlers['register'] = new_user

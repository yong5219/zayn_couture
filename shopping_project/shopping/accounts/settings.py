# -*- coding: utf-8 -*-

from django.conf import settings

gettext = lambda s: s

ACCOUNT_DEFAULT_PRIVACY = getattr(settings, 'ACCOUNT_DEFAULT_PRIVACY', 'registered')

ACCOUNT_PHOTO_SECURE = getattr(settings, 'ACCOUNT_PHOTO_SECURE', settings.USE_HTTPS)

ACCOUNT_PHOTO_DEFAULT = getattr(settings, 'ACCOUNT_PHOTO_DEFAULT', 'mm')

ACCOUNT_PHOTO_GRAVATAR = getattr(settings, 'ACCOUNT_PHOTO_GRAVATAR', True)

ACCOUNT_GRAVATAR_SIZE = getattr(settings, 'ACCOUNT_GRAVATAR_SIZE', 168)

ACCOUNT_ACTIVATED = getattr(settings, 'ACCOUNT_ACTIVATED', 'ALREADY_ACTIVATED')

ACCOUNT_ACTIVATION_DAYS = getattr(settings, 'ACCOUNT_ACTIVATION_DAYS', 7)

ACCOUNT_ACTIVATION_RETRY = getattr(settings, 'ACCOUNT_ACTIVATION_RETRY', True)

ACCOUNT_FORBIDDEN_USERNAMES = getattr(settings, 'ACCOUNT_FORBIDDEN_USERNAMES', ('signup',
    'signout', 'signin', 'activate', 'me', 'password', 'fuck', 'fucker'))

ACCOUNT_ACTIVATION_REQUIRED = getattr(settings, 'ACCOUNT_ACTIVATION_REQUIRED', True)

ACCOUNT_REMEMBER_ME_DAYS = getattr(settings, 'ACCOUNT_REMEMBER_ME_DAYS', (gettext(u'1 month'), 30))

ACCOUNT_SIGNIN_REDIRECT_URL = getattr(settings, 'ACCOUNT_SIGNIN_REDIRECT_URL', '/') #account/%(username)s/

ACCOUNT_REDIRECT_ON_SIGNOUT = getattr(settings, 'ACCOUNT_REDIRECT_ON_SIGNOUT', None)

ACCOUNT_SIGNIN_AFTER_SIGNUP = getattr(settings, 'ACCOUNT_SIGNIN_AFTER_SIGNUP', False)

ACCOUNT_HIDE_EMAIL = getattr(settings, 'ACCOUNT_HIDE_EMAIL', False)

ACCOUNT_DISABLE_PROFILE_LIST = getattr(settings, 'ACCOUNT_DISABLE_PROFILE_LIST', False)

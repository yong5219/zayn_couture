# -*- coding: utf-8 -*-

import random, urllib, datetime
import os

from django.conf import settings
from django.template.defaultfilters import slugify as django_slugify
from django.utils import six
from django.utils.module_loading import import_string
from django.shortcuts import redirect, resolve_url
from django.utils.http import is_safe_url

from unidecode import unidecode


try:
    from hashlib import sha1 as sha_constructor, md5 as md5_constructor
except ImportError:
    from django.utils.hashcompat import sha_constructor, md5_constructor

from accounts import settings as account_settings


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def generate_sha1(string, salt=None):
    """
    Generates a sha1 hash for supplied string.

    :param string:
        The string that needs to be encrypted.

    :param salt:
        Optionally define your own salt. If none is supplied, will use a random
        string of 5 characters.

    :return: Tuple containing the salt and hash.
    """
    if not salt:
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
    hash = sha_constructor(salt+str(string)).hexdigest()

    return (salt, hash)


def get_gravatar(email, size=80, default='identicon'):
    """ Get Gravatar from an email address.

    :param size:
        The size in pixels of one side of the Gravatar's square image.
        Optional, if not supplied will default to ``80``.

    :param default:
        Defines what should be displayed if no image is found for this user.
        Optional argument which defaults to ``identicon``. The argument can be
        a URI to an image or one of the following options:

            ``404``
                Do not load any image if none is associated with the email
                hash, instead return an HTTP 404 (File Not Found) response.

            ``mm``
                Mystery-man, a simple, cartoon-style silhouetted outline of a
                person (does not vary by email hash).

            ``identicon``
                A geometric pattern based on an email hash.

            ``monsterid``
                A generated 'monster' with different colors, faces, etc.

            ``wavatar``
                Generated faces with differing features and backgrounds

            ``retro``
                Awesome generated, 8-bit arcade-style pixelated faces

            ``blank``
                A transparent PNG image (border added to HTML below for demonstration purposes)

    :return: The URI pointing to the Gravatar.

    """
    if account_settings.ACCOUNT_PHOTO_SECURE:
        base_url = 'https://secure.gravatar.com/avatar/'
    else:
        base_url = 'http://www.gravatar.com/avatar/'

    gravatar_url = '%(base_url)s%(gravatar_id)s?' % {'base_url': base_url,
        'gravatar_id': md5_constructor(email.lower()).hexdigest()}

    gravatar_url += urllib.urlencode({'s': str(size),'d': default})
    return gravatar_url


def get_datetime_now():
    """
    Returns datetime object with current point in time.

    In Django 1.4+ it uses Django's django.utils.timezone.now() which returns
    an aware or naive datetime that represents the current point in time
    when ``USE_TZ`` in project's settings is True or False respectively.
    In older versions of Django it uses datetime.datetime.now().
    """
    try:
        from django.utils import timezone
        return timezone.now() # pragma: no cover
    except ImportError: # pragma: no cover
        return datetime.datetime.now()


def get_protocol():
    """
    Returns a string with the current protocol.

    This can be either 'http' or 'https' depending on setting.
    """
    protocol = 'http'
    if settings.USE_HTTPS:
        protocol = 'https'
    return protocol


def signin_redirect(redirect=None, user=None):
    """
    Redirect user after successful sign in.

    First looks for a ``requested_redirect``. If not supplied will fall-back to
    the user specific account page. If all fails, will fall-back to the standard
    Django ``LOGIN_REDIRECT_URL`` setting. Returns a string defining the URI to
    go next.

    :param redirect:
        A value normally supplied by ``next`` form field. Gets preference
        before the default view which requires the user.

    :param user:
        A ``User`` object specifying the user who has just signed in.

    :return: String containing the URI to redirect to.

    """
    if redirect:
        return redirect
    elif user is not None:
        return account_settings.ACCOUNT_SIGNIN_REDIRECT_URL % {'username': user.username}
    else:
        return settings.LOGIN_REDIRECT_URL


## Dig Paginator
import math
from django.core.paginator import \
    Paginator, QuerySetPaginator, Page, InvalidPage

__all__ = (
    'InvalidPage',
    'ExPaginator',
    'DiggPaginator',
    'QuerySetDiggPaginator',
)

# class ExPaginator(Paginator):
#     """Adds a ``softlimit`` option to ``page()``. If True, querying a
#     page number larger than max. will not fail, but instead return the
#     last available page.

#     This is useful when the data source can not provide an exact count
#     at all times (like some search engines), meaning the user could
#     possibly see links to invalid pages at some point which we wouldn't
#     want to fail as 404s.

#     >>> items = range(1, 1000)
#     >>> paginator = ExPaginator(items, 10)
#     >>> paginator.page(1000)
#     Traceback (most recent call last):
#     InvalidPage: That page contains no results
#     >>> paginator.page(1000, softlimit=True)
#     <Page 100 of 100>

#     # [bug] graceful handling of non-int args
#     >>> paginator.page("str")
#     Traceback (most recent call last):
#     InvalidPage: That page number is not an integer
#     """
#     def _ensure_int(self, num, e):
#         # see Django #7307
#         try:
#             return int(num)
#         except ValueError:
#             raise e

#     def page(self, number, softlimit=False):
#         try:
#             return super(ExPaginator, self).page(number)
#         except InvalidPage, e:
#             number = self._ensure_int(number, e)
#             if number > self.num_pages and softlimit:
#                 return self.page(self.num_pages, softlimit=False)
#             else:
# raise e

# class DiggPaginator(ExPaginator):
#     """
#     Based on Django's default paginator, it adds "Digg-style" page ranges
#     with a leading block of pages, an optional middle block, and another
#     block at the end of the page range. They are available as attributes
#     on the page:

#     {# with: page = digg_paginator.page(1) #}
#     {% for num in page.leading_range %} ...
#     {% for num in page.main_range %} ...
#     {% for num in page.trailing_range %} ...

#     Additionally, ``page_range`` contains a nun-numeric ``False`` element
#     for every transition between two ranges.

#     {% for num in page.page_range %}
#         {% if not num %} ...  {# literally output dots #}
#         {% else %}{{ num }}
#         {% endif %}
#     {% endfor %}

#     Additional arguments passed to the constructor allow customization of
#     how those bocks are constructed:

#     body=5, tail=2

#     [1] 2 3 4 5 ... 91 92
#     |_________|     |___|
#     body            tail
#               |_____|
#               margin

#     body=5, tail=2, padding=2

#     1 2 ... 6 7 [8] 9 10 ... 91 92
#             |_|     |__|
#              ^padding^
#     |_|     |__________|     |___|
#     tail    body             tail

#     ``margin`` is the minimum number of pages required between two ranges; if
#     there are less, they are combined into one.

#     When ``align_left`` is set to ``True``, the paginator operates in a
#     special mode that always skips the right tail, e.g. does not display the
#     end block unless necessary. This is useful for situations in which the
#     exact number of items/pages is not actually known.

#     # odd body length
#     >>> print DiggPaginator(range(1,1000), 10, body=5).page(1)
#     1 2 3 4 5 ... 99 100
#     >>> print DiggPaginator(range(1,1000), 10, body=5).page(100)
#     1 2 ... 96 97 98 99 100

#     # even body length
#     >>> print DiggPaginator(range(1,1000), 10, body=6).page(1)
#     1 2 3 4 5 6 ... 99 100
#     >>> print DiggPaginator(range(1,1000), 10, body=6).page(100)
#     1 2 ... 95 96 97 98 99 100

#     # leading range and main range are combined when close; note how
#     # we have varying body and padding values, and their effect.
#     >>> print DiggPaginator(range(1,1000), 10, body=5, padding=2, margin=2).page(3)
#     1 2 3 4 5 ... 99 100
#     >>> print DiggPaginator(range(1,1000), 10, body=6, padding=2, margin=2).page(4)
#     1 2 3 4 5 6 ... 99 100
#     >>> print DiggPaginator(range(1,1000), 10, body=5, padding=1, margin=2).page(6)
#     1 2 3 4 5 6 7 ... 99 100
#     >>> print DiggPaginator(range(1,1000), 10, body=5, padding=2, margin=2).page(7)
#     1 2 ... 5 6 7 8 9 ... 99 100
#     >>> print DiggPaginator(range(1,1000), 10, body=5, padding=1, margin=2).page(7)
#     1 2 ... 5 6 7 8 9 ... 99 100

#     # the trailing range works the same
#     >>> print DiggPaginator(range(1,1000), 10, body=5, padding=2, margin=2, ).page(98)
#     1 2 ... 96 97 98 99 100
#     >>> print DiggPaginator(range(1,1000), 10, body=6, padding=2, margin=2, ).page(97)
#     1 2 ... 95 96 97 98 99 100
#     >>> print DiggPaginator(range(1,1000), 10, body=5, padding=1, margin=2, ).page(95)
#     1 2 ... 94 95 96 97 98 99 100
#     >>> print DiggPaginator(range(1,1000), 10, body=5, padding=2, margin=2, ).page(94)
#     1 2 ... 92 93 94 95 96 ... 99 100
#     >>> print DiggPaginator(range(1,1000), 10, body=5, padding=1, margin=2, ).page(94)
#     1 2 ... 92 93 94 95 96 ... 99 100

#     # all three ranges may be combined as well
#     >>> print DiggPaginator(range(1,151), 10, body=6, padding=2).page(7)
#     1 2 3 4 5 6 7 8 9 ... 14 15
#     >>> print DiggPaginator(range(1,151), 10, body=6, padding=2).page(8)
#     1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
#     >>> print DiggPaginator(range(1,151), 10, body=6, padding=1).page(8)
#     1 2 3 4 5 6 7 8 9 ... 14 15

#     # no leading or trailing ranges might be required if there are only
#     # a very small number of pages
#     >>> print DiggPaginator(range(1,80), 10, body=10).page(1)
#     1 2 3 4 5 6 7 8
#     >>> print DiggPaginator(range(1,80), 10, body=10).page(8)
#     1 2 3 4 5 6 7 8
#     >>> print DiggPaginator(range(1,12), 10, body=5).page(1)
#     1 2

#     # test left align mode
#     >>> print DiggPaginator(range(1,1000), 10, body=5, align_left=True).page(1)
#     1 2 3 4 5
#     >>> print DiggPaginator(range(1,1000), 10, body=5, align_left=True).page(50)
#     1 2 ... 48 49 50 51 52
#     >>> print DiggPaginator(range(1,1000), 10, body=5, align_left=True).page(97)
#     1 2 ... 95 96 97 98 99
#     >>> print DiggPaginator(range(1,1000), 10, body=5, align_left=True).page(100)
#     1 2 ... 96 97 98 99 100

#     # padding: default value
#     >>> DiggPaginator(range(1,1000), 10, body=10).padding
#     4

#     # padding: automatic reduction
#     >>> DiggPaginator(range(1,1000), 10, body=5).padding
#     2
#     >>> DiggPaginator(range(1,1000), 10, body=6).padding
#     2

#     # padding: sanity check
#     >>> DiggPaginator(range(1,1000), 10, body=5, padding=3)
#     Traceback (most recent call last):
#     ValueError: padding too large for body (max 2)
#     """
#     def __init__(self, *args, **kwargs):
#         self.body = kwargs.pop('body', 10)
#         self.tail = kwargs.pop('tail', 2)
#         self.align_left = kwargs.pop('align_left', False)
#         self.margin = kwargs.pop('margin', 4)  # TODO: make the default relative to body?
#         # validate padding value
#         max_padding = int(math.ceil(self.body/2.0)-1)
#         self.padding = kwargs.pop('padding', min(4, max_padding))
#         if self.padding > max_padding:
#             raise ValueError('padding too large for body (max %d)'%max_padding)
#         super(DiggPaginator, self).__init__(*args, **kwargs)

#     def page(self, number, *args, **kwargs):
#         """Return a standard ``Page`` instance with custom, digg-specific
#         page ranges attached.
#         """

#         page = super(DiggPaginator, self).page(number, *args, **kwargs)
#         number = int(number) # we know this will work

#         # easier access
#         num_pages, body, tail, padding, margin = \
#             self.num_pages, self.body, self.tail, self.padding, self.margin

#         # put active page in middle of main range
#         main_range = map(int, [
#             math.floor(number-body/2.0)+1,  # +1 = shift odd body to right
#             math.floor(number+body/2.0)])
#         # adjust bounds
#         if main_range[0] < 1:
#             main_range = map(abs(main_range[0]-1).__add__, main_range)
#         if main_range[1] > num_pages:
#             main_range = map((num_pages-main_range[1]).__add__, main_range)

#         # Determine leading and trailing ranges; if possible and appropriate,
#         # combine them with the main range, in which case the resulting main
#         # block might end up considerable larger than requested. While we
#         # can't guarantee the exact size in those cases, we can at least try
#         # to come as close as possible: we can reduce the other boundary to
#         # max padding, instead of using half the body size, which would
#         # otherwise be the case. If the padding is large enough, this will
#         # of course have no effect.
#         # Example:
#         #     total pages=100, page=4, body=5, (default padding=2)
#         #     1 2 3 [4] 5 6 ... 99 100
#         #     total pages=100, page=4, body=5, padding=1
#         #     1 2 3 [4] 5 ... 99 100
#         # If it were not for this adjustment, both cases would result in the
#         # first output, regardless of the padding value.
#         if main_range[0] <= tail+margin:
#             leading = []
#             main_range = [1, max(body, min(number+padding, main_range[1]))]
#             main_range[0] = 1
#         else:
#             leading = range(1, tail+1)
#         # basically same for trailing range, but not in ``left_align`` mode
#         if self.align_left:
#             trailing = []
#         else:
#             if main_range[1] >= num_pages-(tail+margin)+1:
#                 trailing = []
#                 if not leading:
#                     # ... but handle the special case of neither leading nor
#                     # trailing ranges; otherwise, we would now modify the
#                     # main range low bound, which we just set in the previous
#                     # section, again.
#                     main_range = [1, num_pages]
#                 else:
#                     main_range = [min(num_pages-body+1, max(number-padding, main_range[0])), num_pages]
#             else:
#                 trailing = range(num_pages-tail+1, num_pages+1)

#         # finally, normalize values that are out of bound; this basically
#         # fixes all the things the above code screwed up in the simple case
#         # of few enough pages where one range would suffice.
#         main_range = [max(main_range[0], 1), min(main_range[1], num_pages)]

#         # make the result of our calculations available as custom ranges
#         # on the ``Page`` instance.
#         page.main_range = range(main_range[0], main_range[1]+1)
#         page.leading_range = leading
#         page.trailing_range = trailing
#         page.page_range = reduce(lambda x, y: x+((x and y) and [False])+y,
#             [page.leading_range, page.main_range, page.trailing_range])

#         page.__class__ = DiggPage
#         return page

# class DiggPage(Page):
#     def __str__(self):
#         return " ... ".join(filter(None, [
#                             " ".join(map(str, self.leading_range)),
#                             " ".join(map(str, self.main_range)),
#                             " ".join(map(str, self.trailing_range))]))

# class QuerySetDiggPaginator(DiggPaginator, QuerySetPaginator):
#     pass

if __name__ == "__main__":
    import doctest
    doctest.testmod()

def fetch_resources(uri, rel):
    path = os.path.join(os.path.join(settings.PROJECT_PATH, 'static'),uri.replace(settings.STATIC_URL, ""))
    return path


def default_slugifier(value):
    """
    Oscar's default slugifier function.
    Uses Django's slugify function, but first applies unidecode() to convert
    non-ASCII strings to ASCII equivalents where possible.
    """
    return django_slugify(value)


def slugify(value):
    """
    Slugify a string (even if it contains non-ASCII chars)
    """
    # Re-map some strings to avoid important characters being stripped.  Eg
    # remap 'c++' to 'cpp' otherwise it will become 'c'.
    for k, v in settings.OSCAR_SLUG_MAP.items():
        value = value.replace(k, v)

    # Allow an alternative slugify function to be specified
    # Recommended way to specify a function is as a string
    slugifier = getattr(settings, 'OSCAR_SLUG_FUNCTION', default_slugifier)
    if isinstance(slugifier, six.string_types):
        slugifier = import_string(slugifier)

    # Use unidecode to convert non-ASCII strings to ASCII equivalents where
    # possible.
    value = slugifier(unidecode(six.text_type(value)))

    # Remove stopwords
    for word in settings.OSCAR_SLUG_BLACKLIST:
        value = value.replace(word + '-', '')
        value = value.replace('-' + word, '')

    return value


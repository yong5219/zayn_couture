# -*- coding: utf-8 -*-

import logging

from django.contrib.sites.models import Site
from django.conf import settings
from shopping.utils import get_protocol
from accounts import settings as account_settings
# from templated_email import send_templated_mail

from post_office.models import PRIORITY
from post_office import mail
logger = logging.getLogger(__name__)


# def send_activation_email(self):
#         """
#         Sends a activation email to the user.

#         This email is send when the user wants to activate their newly created
#         user.
#         """
#         # site = Site.objects.get_current()
#         context = {
#             'user': self.user,
#             'protocol': get_protocol(),
#             'activation_days': account_settings.ACCOUNT_ACTIVATION_DAYS,
#             'activation_key': self.activation_key,
#             # 'site': site,
#         }

#         mail.send(
#             [self.user.email,],
#             settings.DEFAULT_FROM_EMAIL,
#             template='account/activation_email',
#             context=context,
#             priority=PRIORITY.medium,
#         )

def send_activation_email(account):
    """
    Thank you email to user, when user submit contact us form
    """
    site = Site.objects.get_current()

    if account:
        TO_EMAIL = account.user.email

        try:
            mail.send(
                [TO_EMAIL, ],
                template='activation_email',
                context={
                    "account": account,
                    "site": site,
                },
                priority=PRIORITY.now,
                # headers={'Reply-to': settings.EMAIL_FOR_CONTACT_US},
            )
        except Exception as e:
            logger.error("Error at contacts_user_thank_you. Reason: {0}".format(e))
    else:
        logger.error("Unexpected error on contacts_user_thank_you")

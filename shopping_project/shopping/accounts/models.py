# -*- coding: utf-8 -*-

import datetime
import re
import os

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string


from post_office.models import PRIORITY
from post_office import mail

from shopping.models import TimeStampedModel
from shopping.utils import generate_sha1, get_gravatar, get_datetime_now, get_protocol
from shopping.emails import send_activation_email
from accounts.managers import AccountSignupManager
from accounts import settings as account_settings
from accounts.choices import STATE_CHOICES, COUNTRY_CHOICES, GENDER_CHOICES


class AccountSignup(TimeStampedModel):
    """
    AccountSignup model which stores all the necessary information to have a full
    functional user implementation on your Django website.
    """
    user = models.OneToOneField(User, verbose_name=_('user'), related_name='user_account_signup')
    last_active = models.DateTimeField(_('last active'), blank=True, null=True,
        help_text=_('The last date that the user was active.'))
    activation_key = models.CharField(_('activation key'), max_length=255, blank=True)
    activation_notification_send = models.BooleanField(_('notification send'), default=False,
        help_text=_('Designates whether this user has already got a notification about activating their account.'))
    email_unconfirmed = models.EmailField(_('unconfirmed email address'), blank=True,
        help_text=_('Temporary email address when the user requests an email change.'))
    email_confirmation_key = models.CharField(_('unconfirmed email verification key'), max_length=40, blank=True)
    email_confirmation_key_created = models.DateTimeField(_('creation date of email confirmation key'),
        blank=True, null=True)

    objects = AccountSignupManager()

    class Meta:
        verbose_name = _('Account registration')
        verbose_name_plural = _('Account registrations')

    def __str__(self):
        return self.user.username

    def change_email(self, email):
        """
        Changes the email address for a user.

        A user needs to verify this new email address before it becomes
        active. By storing the new email address in a temporary field --
        ``temporary_email`` -- we are able to set this email address after the
        user has verified it by clicking on the verification URI in the email.
        This email gets send out by ``send_verification_email``.

        :param email:
            The new email address that the user wants to use.

        """
        self.email_unconfirmed = email

        salt, hash = generate_sha1(self.user.username)
        self.email_confirmation_key = hash
        self.email_confirmation_key_created = get_datetime_now()
        self.save()

        # Send email for activation
        self.send_confirmation_email()

    def send_confirmation_email(self):
        """
        Sends an email to confirm the new email address.

        This method sends out two emails. One to the new email address that
        contains the ``email_confirmation_key`` which is used to verify this
        this email address with :func:`UserenaUser.objects.confirm_email`.

        The other email is to the old email address to let the user know that
        a request is made to change this email address.
        """
        site = Site.objects.get_current()
        context = {
            'user': self.user,
            'new_email': self.email_unconfirmed,
            'protocol': get_protocol(),
            'confirmation_key': self.email_confirmation_key,
            'site': site,
        }

        if self.user.email:
            # Email to the old address, if present
            mail.send(
                [self.user.email, ],
                settings.DEFAULT_FROM_EMAIL,
                template='account/confirmation_email_old',
                context=context,
                priority=PRIORITY.medium,
            )

        # Email to the new address
        mail.send(
            [self.email_unconfirmed, ],
            settings.DEFAULT_FROM_EMAIL,
            template='account/confirmation_email_new',
            context=context,
            priority=PRIORITY.medium,
        )

    def activation_key_expired(self):
        """
        Checks if activation key is expired.

        Returns ``True`` when the ``activation_key`` of the user is expired and
        ``False`` if the key is still valid.

        The key is expired when it's set to the value defined in
        ``ACCOUNT_ACTIVATED`` or ``activation_key_created`` is beyond the
        amount of days defined in ``ACCOUNT_ACTIVATION_DAYS``.
        """
        expiration_days = datetime.timedelta(days=account_settings.ACCOUNT_ACTIVATION_DAYS)
        expiration_date = self.user.date_joined + expiration_days
        if self.activation_key == account_settings.ACCOUNT_ACTIVATED:
            return True
        if get_datetime_now() >= expiration_date:
            return True
        return False


class Profile(TimeStampedModel):
    """
    User profile.
    """
    user = models.OneToOneField(User, unique=True, verbose_name=_('user'), related_name='user_profile')
    gender = models.CharField(_("Gender"), max_length=20, choices=GENDER_CHOICES)
    contact_no = models.CharField(_("Contact No"), max_length=25)
    birth_date = models.DateField(_("Date of Birth"), help_text=_("Format: YYYY-MM-DD"))
    country = models.CharField(_("Country"), max_length=15, default='Malaysia', choices=COUNTRY_CHOICES)
    state = models.CharField(_("State"), max_length=20, choices=STATE_CHOICES)
    address = models.TextField(_("Address"), max_length=255)
    news_letter = models.BooleanField(_("Is Subscribe"), default=False)
    ip_address = models.GenericIPAddressField(_("IP address"), blank=True, null=True)

    def __str__(self):
        return self.user.username

    def get_full_name_or_username(self):
        if self.user.first_name or self.user.last_name:
            name = "%(full_name)s" % {'full_name': self.user.get_full_name()}
        else:
            name = "%(username)s" % {'username': self.user.username}
        return name.strip()

    def _calc_age(self):
        if self.birth_date:
            today = datetime.date.today()

            try:  # raised when birth date is February 29 and the current year is not a leap year
                birthday = self.birth_date.replace(year=today.year)
            except ValueError:
                birthday = self.birth_date.replace(year=today.year, day=self.birth_date.day-1)
            except:
                return 0

            if birthday > today:
                actual_age = today.year - self.birth_date.year - 1
            else:
                actual_age = today.year - self.birth_date.year

            if actual_age < 0:
                return 0
            else:
                return actual_age
        else:
            return 0

    age = property(_calc_age)


@receiver(post_save, sender=AccountSignup)
def activation_email(sender, instance, created, **kwargs):
    account = AccountSignup.objects.get(pk=instance.pk)
    if created:
        send_activation_email(account)
    else:
        pass


def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create user profile when a user is created
    """
    if created:
        new_profile, created = Profile.objects.get_or_create(user=instance)
    else:
        pass

models.signals.post_save.connect(create_user_profile, sender=User)


def create_account_registration(sender, instance, created, **kwargs):
    """
    Automatically create account registration when a user is created by Facebook login
    """
    # print("create account registration")
    # activation_key = get_random_string(64).lower()
    # print(activation_key)
    # print(instance)
    # try:
    #     new_profile, created = AccountSignup.objects.get_or_create(user=instance, activation_key=activation_key)
    # except:
    #     print("Failed")
    # else:
    #     print("created")
    activation_key = get_random_string(64).lower()
    if created:
        new_profile, created = AccountSignup.objects.get_or_create(user=instance, activation_key=activation_key)
    else:
        pass
models.signals.post_save.connect(create_account_registration, sender=User)

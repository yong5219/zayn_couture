# -*- coding: utf-8 -*-

import re

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.models import UserManager, AnonymousUser
from django.utils.crypto import get_random_string

from accounts import settings as account_settings
from accounts import signals as account_signals
from shopping.utils import get_datetime_now, generate_sha1

SHA1_RE = re.compile('^[a-f0-9]{40}$')


class AccountSignupManager(UserManager):
    """ Extra functionality for the AccountSignup model. """

    def create_user(self, username, email, password, active=False, send_email=True):
        """
        A simple wrapper that creates a new :class:`User`.

        :param username:
            String containing the username of the new user.

        :param email:
            String containing the email address of the new user.

        :param password:
            String containing the password for the new user.

        :param active:
            Boolean that defines if the user requires activation by clicking
            on a link in an e-mail. Defaults to ``False``.

        :param send_email:
            Boolean that defines if the user should be sent an email. You could
            set this to ``False`` when you want to create a user in your own
            code, but don't want the user to activate through email.

        :return: :class:`User` instance representing the new user.

        """
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = active
        new_user.save()

        # user_profile = self.create_user_profile(new_user)

        # if send_email:
        #     user_profile.send_activation_email()

        return new_user

    # def create_user_profile(self, user):
    #     """
    #     Creates an :class:`AccountSignup` instance for this user.

    #     :param user:
    #         Django :class:`User` instance.

    #     :return: The newly created :class:`AccountSignup` instance.

    #     """
        # if isinstance(user.username, unicode):
        #     user.username = user.username.encode('utf-8')
        # salt, activation_key = generate_sha1(user.username)
        # activation_key = get_random_string(64).lower()

        # return self.create(user=user, activation_key=activation_key)

    def reissue_activation(self, activation_key):
        """
        Creates a new ``activation_key`` resetting activation timeframe when
        users let the previous key expire.

        :param activation_key:
            String containing the secret SHA1 activation key.

        """
        try:
            signup = self.get(activation_key=activation_key)
        except self.model.DoesNotExist:
            return False
        try:
            salt, new_activation_key = generate_sha1(signup.user.username)
            signup.activation_key = new_activation_key
            signup.save(using=self._db)
            signup.user.date_joined = get_datetime_now()
            signup.user.save(using=self._db)
            signup.send_activation_email()
            return True
        except Exception:
            return False

    def activate_user(self, activation_key):
        """
        Activate an :class:`User` by supplying a valid ``activation_key``.

        If the key is valid and an user is found, activates the user and
        return it. Also sends the ``activation_complete`` signal.

        :param activation_key:
            String containing the secret SHA1 for a valid activation.

        :return:
            The newly activated :class:`User` or ``False`` if not successful.

        """
        # if SHA1_RE.search(activation_key):
        try:
            signup = self.get(activation_key=activation_key)
        except self.model.DoesNotExist:
            return False
        if not signup.activation_key_expired():
            signup.activation_key = account_settings.ACCOUNT_ACTIVATED
            user = signup.user
            user.is_active = True
            signup.save(using=self._db)
            user.save(using=self._db)

            # Send the activation_complete signal
            account_signals.activation_complete.send(sender=None, user=user)

            return user
        # return False

    def check_expired_activation(self, activation_key):
        """
        Check if ``activation_key`` is still valid.

        Raises a ``self.model.DoesNotExist`` exception if key is not present or
         ``activation_key`` is not a valid string

        :param activation_key:
            String containing the secret SHA1 for a valid activation.

        :return:
            True if the ket has expired, False if still valid.

        """
        if SHA1_RE.search(activation_key):
            signup = self.get(activation_key=activation_key)
            return signup.activation_key_expired()
        raise self.model.DoesNotExist

    def confirm_email(self, confirmation_key):
        """
        Confirm an email address by checking a ``confirmation_key``.

        A valid ``confirmation_key`` will set the newly wanted e-mail
        address as the current e-mail address. Returns the user after
        success or ``False`` when the confirmation key is
        invalid. Also sends the ``confirmation_complete`` signal.

        :param confirmation_key:
            String containing the secret SHA1 that is used for verification.

        :return:
            The verified :class:`User` or ``False`` if not successful.
        """
        if SHA1_RE.search(confirmation_key):
            try:
                signup = self.get(email_confirmation_key=confirmation_key, email_unconfirmed__isnull=False)
            except self.model.DoesNotExist:
                return False
            else:
                user = signup.user
                old_email = user.email
                user.email = signup.email_unconfirmed
                signup.email_unconfirmed, signup.email_confirmation_key = '', ''
                signup.save(using=self._db)
                user.save(using=self._db)

                account_signals.confirmation_complete.send(sender=None, user=user, old_email=old_email)

                return user
        return False

    def delete_expired_users(self):
        """
        Checks for expired users and delete's the ``User`` associated with
        it. Skips if the user ``is_staff``.

        :return: A list containing the deleted users.
        """
        deleted_users = []
        for user in User.objects.filter(is_staff=False, is_active=False):
            if user.user_signup.activation_key_expired():
                deleted_users.append(user)
                user.delete()
        return deleted_users


class ProfileManager(models.Manager):
    """ Manager for :class:`Profile` """
    def get_visible_profiles(self, user=None):
        """
        Returns all the visible profiles available to this user.

        For now keeps it simple by just applying the cases when a user is not
        active, a user has it's profile closed to everyone or a user only
        allows registered users to view their profile.

        :param user:
            A Django :class:`User` instance.

        :return:
            All profiles that are visible to this user.

        """
        filter_kwargs = {'user__is_active': True}
        profiles = self.filter(**filter_kwargs)

        if user and isinstance(user, AnonymousUser):
            profiles = profiles.exclude(Q(privacy='onlyme') | Q(privacy='registered'))
        else:
            profiles = profiles.exclude(Q(privacy='onlyme'))

        return profiles

# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

# from smart_selects.form_fields import ChainedModelChoiceField
# from smart_selects.widgets import ChainedSelect

from accounts import settings as account_settings
from accounts.models import AccountSignup, Profile
from accounts.choices import STATE_CHOICES, COUNTRY_CHOICES, GENDER_CHOICES
from shopping.emails import send_activation_email

attrs_dict = {'class': 'form-control'}
attrs_dict_small = {'class': 'form-control input-sm'}
attrs_dict_reg = {'class': 'v-form form-control'}
attrs_dict_login = {'class': 'v-form form-control'}
attrs_dict_rem = {'class': 'login-checkbox'}
USERNAME_RE = r'^[\.\w]+$'


class SignupForm(forms.Form):
    """
    Form for creating a new user account.

    Validates that the requested username and e-mail is not already in use.
    Also requires the password to be entered twice.
    """
    username = forms.RegexField(widget=forms.TextInput(attrs=dict(attrs_dict_reg, placeholder=_(u"Username"), maxlength=30)),label=_(u"Username"), regex=USERNAME_RE, max_length=30, error_messages={"invalid": _(u"Username must contain only letters, numbers, dots and underscores.")})
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict_reg, placeholder=_(u"Email"), maxlength=75)), label=_(u"Email"), max_length=75)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=dict(attrs_dict_reg, placeholder=_(u"Password")), render_value=False), label=_(u"Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=dict(attrs_dict_reg, placeholder=_(u"Confirm Password")), render_value=False), label=_(u"Confirm Password"))
    gender = forms.ChoiceField(widget=forms.Select(attrs=dict(attrs_dict_reg, placeholder=_(u"Gender"))), label=_(u"Gender"), choices=GENDER_CHOICES)
    contact_no = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict_reg, placeholder=_(u"Contact No"))), label=_(u"Contact No"), max_length=20)
    # birth_date = forms.DateField(label=u'Date Of Birth', input_formats='%d/%m/%Y', required=False, widget=forms.DateInput(format='%d/%m/%Y'))
    address = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict_reg, placeholder=_(u"Address"))), label=_(u"Address"), max_length=20)
    state = forms.ChoiceField(widget=forms.Select(attrs=dict(attrs_dict_reg, placeholder=_(u"State"))), label=_(u"State"), choices=STATE_CHOICES)
    country = forms.ChoiceField(widget=forms.Select(attrs=dict(attrs_dict_reg, placeholder=_(u"Country"))), label=_(u"Country"), choices=COUNTRY_CHOICES)
    news_letter = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    tos = forms.BooleanField(widget=forms.CheckboxInput(),
        label=mark_safe(_(u'I have read and agree with the usage <a href="/terms_conditions/" target="_blank"> Terms and Conditions </a>')),
        error_messages={'required': _(u'You must agree to the Terms and Conditions')})

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already in use.
        Also validates that the username is not listed in
        ``ACCOUNT_FORBIDDEN_USERNAMES`` list.
        """
        try:
            User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            pass
        else:
            if AccountSignup.objects.filter(user__username__iexact=self.cleaned_data['username']).exclude(activation_key=account_settings.ACCOUNT_ACTIVATED):
                raise forms.ValidationError(_('This username is already taken but not confirmed. Please check you email for verification steps.'))
            raise forms.ValidationError(_('This username is already taken.'))
        if self.cleaned_data['username'].lower() in account_settings.ACCOUNT_FORBIDDEN_USERNAMES:
            raise forms.ValidationError(_('This username is not allowed.'))
        return self.cleaned_data['username']

    def clean_email(self):
        """
        Validate that the e-mail address is unique.
        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            if AccountSignup.objects.filter(user__email__iexact=self.cleaned_data['email']).exclude(activation_key=account_settings.ACCOUNT_ACTIVATED):
                raise forms.ValidationError(_('This email is already in use but not confirmed. Please check you email for verification steps.'))
            raise forms.ValidationError(_('This email is already in use. Please supply a different email.'))
        return self.cleaned_data['email']

    def clean(self):
        """
        Validates that the values entered into the two password fields match.
        Note that an error here will end up in ``non_field_errors()`` because
        it doesn't apply to a single field.
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_('The two password fields didn\'t match.'))
        return self.cleaned_data

    def save(self):
        """
        Creates a new user and account. Returns the newly created user.
        """
        username, email, password = (
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password1']
        )
        new_user = AccountSignup.objects.create_user(
            username, email, password,
            not account_settings.ACCOUNT_ACTIVATION_REQUIRED,
            account_settings.ACCOUNT_ACTIVATION_REQUIRED
        )

        new_profile = new_user.user_profile
        new_profile.user.username, new_profile.state, new_profile.gender, new_profile.country, new_profile.contact_no, new_profile.address, new_profile.news_letter = (
            self.cleaned_data['username'],
            self.cleaned_data['state'],
            self.cleaned_data['gender'],
            self.cleaned_data['country'],
            self.cleaned_data['contact_no'],
            self.cleaned_data['address'],
            self.cleaned_data['news_letter'],
        )
        new_profile.save()
        # send_activation_email(new_user)
        return new_user


def identification_field_factory(label, error_required):
    """
    A simple identification field factory which enable you to set the label.

    :param label:
        String containing the label for this field.

    :param error_required:
        String containing the error message if the field is left empty.
    """
    return forms.CharField(label=label, widget=forms.TextInput(attrs=dict(attrs_dict_login, placeholder=label)), max_length=75,
        error_messages={'required': _("%(error)s") % {'error': error_required}})


class AuthenticationForm(forms.Form):
    """
    A custom form where the identification can be a e-mail address or username.
    """
    identification = identification_field_factory(_(u"Your username"),  _(u"Please enter username"))
    password = forms.CharField(label=_(u"Password"), widget=forms.PasswordInput(attrs=dict(attrs_dict_login, placeholder=_(u"Password")), render_value=False))
    remember_me = forms.BooleanField(widget=forms.CheckboxInput(), required=False,
        label=_(u'Stay signed in for %(days)s') % {'days': _(account_settings.ACCOUNT_REMEMBER_ME_DAYS[0])})

    def __init__(self, *args, **kwargs):
        """
        A custom init because we need to change the label if no usernames is used
        """
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        # Dirty hack, somehow the label doesn't get translated without declaring
        # it again here.
        self.fields['remember_me'].label = _(u'Remember Me') % {'days': _(account_settings.ACCOUNT_REMEMBER_ME_DAYS[0])}
        self.fields['identification'] = identification_field_factory(_(u"Username"), _(u"Please enter username"))

    def clean(self):
        """
        Checks for the identification and password.
        If the combination can't be found will raise an invalid sign in error.
        """
        identification = self.cleaned_data.get('identification')
        password = self.cleaned_data.get('password')

        if identification and password:
            user = authenticate(username=identification, password=password)
            if user is None:
                raise forms.ValidationError(_(u"Please enter a correct username or email and password. Note that both fields are case-sensitive."))
        return self.cleaned_data


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "password"
        ]


class ChangeEmailForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=75)), label=_(u"New Email"))

    # def __init__(self, user, *args, **kwargs):
    #     """
    #     The current ``user`` is needed for initialisation of this form so
    #     that we can check if the email address is still free and not always
    #     returning ``True`` for this query because it's the users own e-mail
    #     address.
    #     """
    #     super(ChangeEmailForm, self).__init__(*args, **kwargs)
    #     if not isinstance(user, User):
    #         raise TypeError, "user must be an instance of %s" % User.__name__
    #     else:
    #         self.user = user

    def clean_email(self):
        """
        Validate that the email is not already registered with another user
        """
        if self.cleaned_data['email'].lower() == self.user.email:
            raise forms.ValidationError(_(u'You\'re already known under this email.'))
        if User.objects.filter(email__iexact=self.cleaned_data['email']).exclude(email__iexact=self.user.email):
            raise forms.ValidationError(_(u'This email is already in use. Please supply a different email.'))
        return self.cleaned_data['email']

    def save(self):
        """
        Save method calls :func:`user.change_email()` method which sends out an
        email with an verification key to verify and with it enable this new
        email address.
        """

        return self.user.user_account_signup.change_email(self.cleaned_data['email'])


class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user', 'ip_address')

import hashlib

from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.models import User
from django.views.generic.edit import FormView, UpdateView
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout, REDIRECT_FIELD_NAME
from django.views.generic import TemplateView
from django.contrib import messages
from django.views.generic.list import ListView
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic.base import RedirectView
from django.contrib.messages.views import SuccessMessageMixin

from accounts import signals as account_signals
from accounts import settings as account_settings
from shopping.utils import signin_redirect
from accounts.forms import SignupForm, AuthenticationForm, UpdateProfileForm
from accounts.models import Profile, AccountSignup
# from articles.models import Article


class ExtraContextTemplateView(TemplateView):
    """ Add extra context to a simple template view """
    extra_context = None

    def get_context_data(self, *args, **kwargs):
        context = super(ExtraContextTemplateView, self).get_context_data(*args, **kwargs)
        if self.extra_context:
            context.update(self.extra_context)
        return context

    # this view is used in POST requests, e.g. signup when the form is not valid
    post = TemplateView.get


class SignUpFormView(FormView):
    form_class = SignupForm
    template_name = 'accounts/signup.html'

    def form_valid(self, form, success_url=None, extra_context=None, template_name=template_name):
        user = form.save()

        # Send the signup complete signal
        account_signals.signup_complete.send(sender=None, user=user)

        if success_url:
            redirect_to = success_url
        else:
            redirect_to = reverse('account_signup_complete', kwargs={'username': user.username})

        # A new signed user should logout the old one.
        if self.request.user.is_authenticated():
            logout(self.request)

        if (account_settings.ACCOUNT_SIGNIN_AFTER_SIGNUP and not account_settings.ACCOUNT_ACTIVATION_REQUIRED):
            user = authenticate(identification=user.email, check_password=False)
            login(self.request, user)

        return redirect(redirect_to)

        if not extra_context:
            extra_context = dict()
        extra_context['form'] = form
        return ExtraContextTemplateView.as_view(template_name=template_name, extra_context=extra_context)(self.request)


def direct_to_user_template(request, username, template_name, extra_context=None):
    """
    Simple wrapper for Django's :func:`direct_to_template` view.

    This view is used when you want to show a template to a specific user. A
    wrapper for :func:`direct_to_template` where the template also has access to
    the user that is found with ``username``. For ex. used after signup,
    activation and confirmation of a new e-mail.

    :param username:
        String defining the username of the user that made the action.

    :param template_name:
        String defining the name of the template to use. Defaults to
        ``account/signup_complete.html``.

    **Keyword arguments**

    ``extra_context``
        A dictionary containing extra variables that should be passed to the
        rendered template. The ``account`` key is always the ``User``
        that completed the action.

    **Extra context**

    ``viewed_user``
        The currently :class:`User` that is viewed.

    """
    user = get_object_or_404(User, username__iexact=username)

    if not extra_context: extra_context = dict()
    extra_context['viewed_user'] = user
    extra_context['profile'] = user.user_profile
    return ExtraContextTemplateView.as_view(template_name=template_name, extra_context=extra_context)(request)


class SignInFormView(SuccessMessageMixin, FormView):
    form_class = AuthenticationForm
    template_name = 'accounts/signin.html'
    success_url = reverse_lazy('accounts:index')
    success_message = "You have been signed in."

    def form_valid(self, form, redirect_field_name=REDIRECT_FIELD_NAME, redirect_signin_function=signin_redirect):
        identification, password, remember_me = (form.cleaned_data['identification'], form.cleaned_data['password'], form.cleaned_data['remember_me'])
        user = authenticate(username=identification, password=password)
        if user.is_active:
            login(self.request, user)
            if remember_me:
                self.request.session.set_expiry(account_settings.ACCOUNT_REMEMBER_ME_DAYS[1] * 86400)
            else:
                self.request.session.set_expiry(0)

            messages.success(self.request, _('You have been signed in.'), fail_silently=True)

            # Whereto now?
            # redirect_to = redirect_signin_function(self.request.REQUEST.get(redirect_field_name), user)
            return HttpResponseRedirect("/")
        else:
            return redirect(reverse('account_disabled', kwargs={'username': user.username}))

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SignInFormView, self).get_context_data(**kwargs)
        return context


class SignOut(RedirectView):

    permanent = False
    query_string = True

    def get_redirect_url(self):
        logout(self.request)
        messages.success(self.request, 'You have been signed out.')
        return reverse('home')


class UserProfile(ListView):
    template_name = 'accounts/profile.html'
    model = Profile

    def get_queryset(self, user=None):
        self.user = get_object_or_404(Profile, user__username=self.kwargs['user'])

    def get_context_data(self, **kwargs):
        context = super(UserProfile, self).get_context_data(**kwargs)
        context['profile'] = Profile.objects.get(user__username=self.user)
        context['object'] = self.user
        context['selected_page'] = "index"

        return context


class ProfileUpdate(SuccessMessageMixin, UpdateView):
    model = Profile
    success_url = reverse_lazy('home')
    form_class = UpdateProfileForm
    success_message = "Profile updated successfully"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProfileUpdate, self).get_context_data(**kwargs)
        return context

from django.shortcuts import render, redirect


def members(request):
    # context = {}
    # template = 'home.html'
    return redirect('/')


def activate(request, activation_key, template_name='accounts/activate_fail.html',
    retry_template_name='account/activate_retry.html', success_url=None, extra_context=None):
    """
    Activate a user with an activation key.

    The key is a SHA1 string. When the SHA1 is found with an
    :class:`AccountSignup`, the :class:`User` of that account will be
    activated.  After a successful activation the view will redirect to
    ``success_url``.  If the SHA1 is not found, the user will be shown the
    ``template_name`` template displaying a fail message.
    If the SHA1 is found but expired, ``retry_template_name`` is used instead,
    so the user can proceed to :func:`activate_retry` to get a new actvation key.

    :param activation_key:
        String of a SHA1 string of 40 characters long. A SHA1 is always 160bit
        long, with 4 bits per character this makes it --160/4-- 40 characters
        long.

    :param template_name:
        String containing the template name that is used when the
        ``activation_key`` is invalid and the activation fails. Defaults to
        ``accounts/activate_fail.html``.

    :param retry_template_name:
        String containing the template name that is used when the
        ``activation_key`` is expired. Defaults to
        ``account/activate_retry.html``.

    :param success_url:
        String containing the URL where the user should be redirected to after
        a successful activation. Will replace ``%(username)s`` with string
        formatting if supplied. If ``success_url`` is left empty, will direct
        to ``account_profile_activity_log`` view.

    :param extra_context:
        Dictionary containing variables which could be added to the template
        context. Default to an empty dictionary.

    """
    try:
        # if (not AccountSignup.objects.check_expired_activation(activation_key) or not account_settings.ACCOUNT_ACTIVATION_RETRY):
        user = AccountSignup.objects.activate_user(activation_key)
        print(user)
        if user:
            # Sign the user in.
            # auth_user = authenticate(username=user, check_password=False)
            # print(auth_user)
            # login(request, auth_user)

            messages.success(request, _('Your account has been activated and you can signin now.'), fail_silently=True)

            # if success_url:
            #     redirect_to = success_url % {'username': user.username}
            # else:
            #     redirect_to = reverse('account_all_profile', kwargs={'user': user.username})
            return redirect('home')
        else:
            if not extra_context:
                extra_context = dict()
            return ExtraContextTemplateView.as_view(template_name=template_name, extra_context=extra_context)(request)
        # else:
        #     if not extra_context:
        #         extra_context = dict()
        #     extra_context['activation_key'] = activation_key
        #     return ExtraContextTemplateView.as_view(template_name=retry_template_name, extra_context=extra_context)(request)
    except AccountSignup.DoesNotExist:
        if not extra_context:
            extra_context = dict()
        return ExtraContextTemplateView.as_view(template_name=template_name, extra_context=extra_context)(request)

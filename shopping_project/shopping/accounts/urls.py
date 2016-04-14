# -*- coding: utf-8 -*-

"""shopping URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import patterns, url
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from accounts import settings as account_settings
from .views import SignUpFormView, SignOut, SignInFormView, ProfileUpdate, activate, direct_to_user_template, UserProfile

urlpatterns = [
    # Signup, signin and signout
    url(r'^signup/$', SignUpFormView.as_view(), name='account_signup'),
    url(r'^signin/$', SignInFormView.as_view(), name='account_signin'),
    # url(r'^signin/$', 'signin', name='account_signin'),
    url(r'^signout/$', SignOut.as_view(), name='account_signout'),

    # account profile
    url(r'^profile/(?P<user>[a-zA-Z0-9-]+)/$', UserProfile.as_view(), name='account_user_profile'),

    #update account profile
    url(r'^update/(?P<pk>\d+)/$', login_required(ProfileUpdate.as_view()), name='account_update'),

    # Signup
    # url(r'^signup/complete/$', TemplateView.as_view(template_name='accounts/signup_complete.html'), name="signup_complete"),
    url(r'^(?P<username>[\.\w-]+)/signup/complete/$',
        direct_to_user_template, {'template_name': 'accounts/signup_complete.html',
        'extra_context': {'account_activation_required': account_settings.ACCOUNT_ACTIVATION_REQUIRED,
        'account_activation_days': account_settings.ACCOUNT_ACTIVATION_DAYS}}, name='account_signup_complete'),

    # Activate
    url(r'^activate/(?P<activation_key>\w+)/$', activate, name='account_activate'),
]

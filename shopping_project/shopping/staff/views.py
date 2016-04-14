from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic.edit import FormView
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate, login, logout, REDIRECT_FIELD_NAME
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic.base import RedirectView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts import settings as account_settings
from shopping.utils import signin_redirect
from accounts.forms import AuthenticationForm, UpdateProfileForm
from products.models import Product
# from articles.models import Article
# Create your views here.


class SignInFormView(SuccessMessageMixin, FormView):
    form_class = AuthenticationForm
    template_name = 'staff/signin.html'
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
            return HttpResponseRedirect("/seller/product_list")
        else:
            return redirect(reverse('account_disabled', kwargs={'username': user.username}))

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SignInFormView, self).get_context_data(**kwargs)
        return context


class SellerProductList(LoginRequiredMixin, ListView):
    login_url = '/seller/signin/'
    template_name = 'staff/product_list.html'
    model = Product
    paginate_by = 10

    def get_queryset(self, slug=None):
        search = self.request.GET.get('search', '')
        object_list = self.model.objects.filter(user=self.request.user)
        if search:
            object_list = self.model.objects.filter(Q(name__icontains=search) | Q(price__icontains=search) | Q(discount_price__icontains=search), user=self.request.user)
        else:
            object_list = self.model.objects.filter(user=self.request.user)
        return object_list

    def get_context_data(self, **kwargs):
        context = super(SellerProductList, self).get_context_data(**kwargs)
        context['products'] = Product.objects.filter(user=self.request.user)
        context['selected_menu'] = "staff_product"
        search = self.request.GET.get('search', '')
        context['user'] = self.request.user
        if search:
            context['search'] = search
        return context


class SellerProductDetail(LoginRequiredMixin, DetailView):
    login_url = '/seller/signin/'
    template_name = 'staff/product_detail.html'
    model = Product

    def get_queryset(self):
        object_list = super(SellerProductDetail, self).get_queryset()
        return object_list.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(SellerProductDetail, self).get_context_data(**kwargs)
        context['selected_menu'] = "staff_product"
        return context

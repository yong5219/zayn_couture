from django.views.generic import FormView

from django import shortcuts
from django.contrib import messages
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from order_cart.forms import AddToCartForm
from order_cart.models import OrderCart, Line
from products.models import Product


class CartAddView(FormView):
    form_class = AddToCartForm
    product_model = Product
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        self.product = shortcuts.get_object_or_404(
            self.product_model, pk=kwargs['pk'])
        return super(CartAddView, self).post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CartAddView, self).get_form_kwargs()
        kwargs['basket'] = self.request.basket
        kwargs['product'] = self.product
        return kwargs


def Add(request):
    # get product pk from html form hidden field
    page_product_pk = request.POST['_method']

    order_cart = OrderCart.objects.get_current_cart(request.user)
    # get the order cart assign for add line into the order cart
    cart = OrderCart.objects.get(pk=order_cart.pk)

    standalone_product = Product.objects.get(pk=page_product_pk)
    if standalone_product.structure == "standalone":

        product = Product.objects.get(pk=standalone_product.pk)

        # check is the line is existing, if yes show error message else show success message
        exists_line = Line.objects.filter(product__id=product.id, cart__id=cart.id).exists()
        if exists_line:
            messages.error(request, u'This product already in your shopping cart, please check your shopping cart.')
        else:
            Line.objects.get_current_line(product, cart)
            messages.success(request, u'This product has been added to your shopping cart.')
    else:
        # if product is parent and have child
        product_id = request.POST['variety_dropdown']
        if product_id != "None":
            product = Product.objects.get(pk=product_id)

            # check is the line is existing, if yes show error message else show success message
            exists_line = Line.objects.filter(product__id=product_id).exists()
            if exists_line:
                messages.error(request, u'This product size already in your shopping cart, please check your shopping cart.')
            else:
                Line.objects.get_current_line(product, cart)
                messages.success(request, u'This product has been added to your shopping cart.')
        else:
            messages.error(request, u'Please select a product size.')

    # after function done return the page to the current product detail page
    return redirect('product_detail', pk=page_product_pk)


@login_required
def List(request):
    cart = OrderCart.objects.get_current_cart(request.user)

    context = {
        'cart': cart,
    }
    return render_to_response('order_cart/cart_detail.html', context, RequestContext(request))

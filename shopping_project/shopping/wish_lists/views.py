from django.views.generic import FormView

from django import shortcuts
from django.contrib import messages
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from order_cart.forms import AddToCartForm
from wish_lists.models import WishList, WishListProduct
from products.models import Product


def Add(request, pk):
    # get product pk from html form hidden field

    wish_list = WishList.objects.get_current_wish_list(request.user)
    product = Product.objects.get(pk=pk)

    # check is the WishListProduct is existing, if yes show error message else show success message
    exists_product = WishListProduct.objects.filter(product__id=pk, wish_list__id=wish_list.id).exists()
    if exists_product:
        messages.error(request, u'This product already in your wish list.')
    else:
        WishListProduct.objects.get_current_wish_list_product(product, wish_list)
        messages.success(request, u'This product has been success add to wish list.')

    # after function done return the page to the current product detail page
    return redirect('product_detail', pk=pk)


@login_required
def List(request):
    wish_list = WishList.objects.get_current_wish_list(request.user)

    context = {
        'wish_list': wish_list,
    }
    return render_to_response('wish_lists/wish_list.html', context, RequestContext(request))

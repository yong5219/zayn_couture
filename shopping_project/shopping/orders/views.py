# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from orders.forms import CheckOutForm
from order_cart.models import OrderCart

# Create your views here.


@login_required
def checkout(request):
    order_cart = OrderCart.objects.get_current_cart(request.user)
    if order_cart.lines.count() > 0:
        form = CheckOutForm(initial={'cart': order_cart.pk, 'user': order_cart.owner.pk, })
        print(request.user.pk)
        if request.method == 'POST':
            form = CheckOutForm(request.POST, initial={'cart': order_cart.pk, 'user': order_cart.owner.pk, })
            if form.is_valid():
                form.price = int('100')
                form.save(user=request.user, cart=order_cart)
                messages.success(request, u'Order had been successful.')
                return redirect('home')
            else:
                messages.error(request, u'Order failed. Please try again!')
                # print form.errors
    else:
        messages.error(request, u'Your have no product in your order cart.')
        return redirect('cart_list')
    context = {
        'form': form,
        'order_cart': order_cart,
    }

    return render_to_response('order/checkout.html', context, RequestContext(request))

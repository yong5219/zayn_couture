# -*- coding: utf-8 -*-
import requests

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect

from orders.forms import CheckOutForm
from order_cart.models import OrderCart

# Create your views here.


@login_required
def checkout(request):
    order_cart = OrderCart.objects.get_current_cart(request.user)
    if order_cart.lines.count() > 0:
        form = CheckOutForm(initial={'cart': order_cart.pk, 'user': order_cart.owner.pk, })

        if request.method == 'POST':
            form = CheckOutForm(request.POST, initial={'cart': order_cart.pk, 'user': order_cart.owner.pk, })
            if form.is_valid():
                payload = {'MerchantCode': 'M03228', 'PaymentId': '', 'RefNo': 'A00000001', 'Amount': '1.00', 'Currency': 'MYR', 'ProdDesc': 'clothing product',
                            'UserName': 'testinguser', 'UserEmail': 'yong_5219@hotmail.com', 'UserContact': '0162926391', 'Remark': '', 'Lang': 'UTF-8', 'Signature': 'value2',
                            'ResponseURL': 'http://zayncouture.webfactional.com/order/checkout/', 'BackendURL': ''}
                r = requests.get('https://www.mobile88.com/ePayment/entry.asp', params=payload)
                return HttpResponseRedirect(r.url)

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

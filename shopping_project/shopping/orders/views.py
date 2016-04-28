# -*- coding: utf-8 -*-
import requests
import httplib2
import urllib

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from orders.forms import CheckOutForm
from order_cart.models import OrderCart

# Create your views here.


@login_required
@csrf_exempt
def checkout(request):
    order_cart = OrderCart.objects.get_current_cart(request.user)
    if order_cart.lines.count() > 0:
        form = CheckOutForm(initial={'cart': order_cart.pk, 'user': order_cart.owner.pk, })

        if request.method == 'POST':

            form = CheckOutForm(request.POST, initial={'cart': order_cart.pk, 'user': order_cart.owner.pk, })
            if form.is_valid():
                # payload = {'MerchantCode': 'M03228', 'PaymentId': '', 'RefNo': 'A00000001', 'Amount': '1.00',
                #             'Currency': 'MYR', 'ProdDesc': 'clothing product', 'UserName': 'testinguser',
                #             'UserEmail': 'yong_5219@hotmail.com', 'UserContact': '0162926391', 'Remark': '',
                #             'Lang': 'UTF-8', 'Signature': '84dNMbfgjLMS42IqSTPqQ99cUGA',
                #             'ResponseURL': 'http://zayncouture.webfactional.com/order/checkout-postback/', 'BackendURL': ''}
                # r = requests.post('https://www.mobile88.com/ePayment/entry.asp', params=payload)
                # return HttpResponseRedirect(r.url)

                data = {'MerchantCode': 'M03228', 'PaymentId': '', 'RefNo': 'A00000001', 'Amount': '1.00',
                            'Currency': 'MYR', 'ProdDesc': 'clothing product', 'UserName': 'testinguser',
                            'UserEmail': 'yong_5219@hotmail.com', 'UserContact': '0162926391', 'Remark': '',
                            'Lang': 'UTF-8', 'Signature': '84dNMbfgjLMS42IqSTPqQ99cUGA',
                            'ResponseURL': 'http://zayncouture.webfactional.com/order/checkout-postback/', 'BackendURL': ''}
                body = urllib.urlencode(data)
                h = httplib2.Http()
                resp, content = h.request("https://www.mobile88.com/ePayment/entry.asp", method="POST", body=body)
                # return HttpResponseRedirect(content)

                # if status == 1:
                #     form.save(user=request.user, cart=order_cart)
                #     messages.success(request, u'Order had been successful.')
                #     return redirect('home')
                # else:
                #     messages.error(request, u'Order failed. Please try again!1')
            else:
                messages.error(request, u'Order failed. Please try again!1')
                # print form.errors
    else:
        messages.error(request, u'Your have no product in your order cart.')
        return redirect('cart_list')
    context = {
        'form': form,
        'order_cart': order_cart,
    }

    return render_to_response('order/checkout.html', context, RequestContext(request))


@login_required
@csrf_exempt
def checkout_postback(request):
    order_cart = OrderCart.objects.get_current_cart(request.user)
    if order_cart.lines.count() > 0:
        form = CheckOutForm(initial={'cart': order_cart.pk, 'user': order_cart.owner.pk, })

        if request.method == 'POST':
            # return redirect('home')
            status = request.POST['Status']
            errdesc = request.POST['ErrDesc']
            transid = request.POST['TransId']
            form = CheckOutForm(request.POST, initial={'cart': order_cart.pk, 'user': order_cart.owner.pk, })
            if form.is_valid():

                status = request.POST['Status']

                if status == "1":
                    form.save(user=request.user, cart=order_cart)
                    messages.success(request, u'Order had been successful.')
                    return redirect('home')
                else:
                    messages.error(request, u'Order failed. Please try again!2')
                return redirect('cart_list')
            else:
                messages.error(request, u'[%s][%s][%s]Order failed. Please try again!3' % (status, errdesc, transid))
                return redirect('cart_list')
                # print form.errors
    else:
        messages.error(request, u'Your have no product in your order cart.')
        return redirect('cart_list')
    context = {
        'form': form,
        'order_cart': order_cart,
    }

    return render_to_response('order/checkout.html', context, RequestContext(request))

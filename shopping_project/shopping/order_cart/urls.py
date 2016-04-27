from django.conf.urls import patterns, url

from order_cart.views import List

urlpatterns = patterns(
    'order_cart.views',
    url(r'^add/$', 'Add', name='cart_add'),
    url(r'^list/$', 'List', name='cart_list'),
    url(r'^remove/$', 'DeleteLine', name='cart_remove_line')

)

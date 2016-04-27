from django.conf.urls import patterns, url

urlpatterns = patterns(
    'orders.views',
    url(r'^checkout/$', 'checkout', name='order_checkout'),
)

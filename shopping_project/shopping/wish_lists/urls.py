from django.conf.urls import patterns, url


urlpatterns = patterns(
    'wish_lists.views',
    url(r'^add/(?P<pk>\d+)/$', 'Add', name='wish_list_add'),
    url(r'^list/$', 'List', name='wish_list_list'),

)

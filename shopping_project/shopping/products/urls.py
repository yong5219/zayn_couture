from django.conf.urls import patterns, url

from products.views import ProductList, ProductDetail

urlpatterns = patterns(
    '',
    # url(r'^$', views.index, name='index'),
    url(r'^list/(?P<slug>[a-zA-Z0-9-]+)/$', ProductList.as_view(), name='product_list'),
    # url(r'^add/$', ArticleCreate.as_view(), name="articles_article_add"),
    # url(r'^detail/json/$', ArticleLikeDislikeDetail.as_view(), name='articles_article_like_dislike_detail'),
    # url(r'^detail/json/delete/$', ArticleDeleteLikeDislikeDetail.as_view(), name='articles_article_delete_like_dislike_detail'),
    url(r'^detail/(?P<pk>\d+)/$', ProductDetail.as_view(), name='product_detail'),

)

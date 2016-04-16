from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from shopping.models import TimeStampedModel
from products.models import Product


class WishListManager(models.Manager):
    def get_current_wish_list(self, user):
        wish_list = super(WishListManager, self).get_queryset().filter(user=user)
        if len(wish_list) == 0:
            wish_list, created = super(WishListManager, self).get_queryset().get_or_create(user=user)
        elif len(wish_list) == 1:
            wish_list = wish_list[0]
        return wish_list


class WishList(TimeStampedModel):
    """
    Wish List
    """
    user = models.ForeignKey(User)
    objects = WishListManager()

    # def __str__(self):
    #     return self.user


class WishListProductManager(models.Manager):
    def get_current_wish_list_product(self, product, wish_list):
        line = super(WishListProductManager, self).get_queryset().filter(product=product, wish_list=wish_list)
        if len(line) == 0:
            line, created = super(WishListProductManager, self).get_queryset().get_or_create(product=product, wish_list=wish_list)
        elif len(line) == 1:
            line = line[0]
        return line


class WishListProduct(TimeStampedModel):
    """
    Wish List Product
    """
    wish_list = models.ForeignKey(WishList, related_name="wish_list")
    product = models.ForeignKey(Product, related_name="wish_list_product")
    objects = WishListProductManager()
    # def __str__(self):
    #     return self.order

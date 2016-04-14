from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from shopping.models import TimeStampedModel
from products.models import Product, UOM


class Order(TimeStampedModel):
    """
    Order
    """
    user = models.ForeignKey(User)
    price = models.DecimalField(_("Total Price"), max_digits=11, decimal_places=2, default=0)
    delivery_price = models.DecimalField(_("Delivery Price"), max_digits=11, decimal_places=2, default=0)
    discount_price = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    remark = models.TextField(_("Remark"), blank=True, null=True, max_length=255)
    order_date = models.DateTimeField(_("Order Date"))
    is_paid = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.user


class OrderProduct(TimeStampedModel):
    """
    Order Product
    """
    order = models.ForeignKey(Order, related_name="order_product_order")
    product = models.ForeignKey(Product, related_name="order_product_product")
    uom = models.ForeignKey(UOM, related_name='order_product_uom')
    quantity = models.PositiveIntegerField(_('Quantity'), default=0)
    price = models.DecimalField(_("Product Price"), max_digits=11, decimal_places=2, default=0)

    # def __str__(self):
    #     return self.order

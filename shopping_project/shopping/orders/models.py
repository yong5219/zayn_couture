from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.utils.translation import pgettext_lazy

from shopping.models import TimeStampedModel
from products.models import Product, UOM
from order_cart.models import OrderCart


class Order(TimeStampedModel):
    """
    Order
    """
    user = models.ForeignKey(User)
    cart = models.ForeignKey(OrderCart)
    MR, MISS, MRS, MS, DR = ('Mr', 'Miss', 'Mrs', 'Ms', 'Dr')
    TITLE_CHOICES = (
        (MR, _("Mr")),
        (MISS, _("Miss")),
        (MRS, _("Mrs")),
        (MS, _("Ms")),
        (DR, _("Dr")),
    )

    title = models.CharField(
        pgettext_lazy(u"Treatment Pronouns for the customer", u"Title"),
        max_length=64, choices=TITLE_CHOICES)
    first_name = models.CharField(_("First name"), max_length=255)
    last_name = models.CharField(_("Last name"), max_length=255)
    contact_no = models.CharField(_("Contact No"), max_length=25)
    # We use quite a few lines of an address as they are often quite long and
    # it's easier to just hide the unnecessary ones than add extra ones.
    line1 = models.CharField(_("First line of address"), max_length=255)
    line2 = models.CharField(
        _("Second line of address"), max_length=255, blank=True)
    line3 = models.CharField(
        _("Third line of address"), max_length=255, blank=True)
    line4 = models.CharField(_("City"), max_length=255, blank=True)
    state = models.CharField(_("State/County"), max_length=255)
    postcode = models.CharField(
        _("Post/Zip-code"), max_length=64)
    remark = models.TextField(_("Remark"), blank=True, null=True, max_length=255)
    price = models.DecimalField(_("Total Price"), max_digits=11, decimal_places=2, default=0)
    delivery_price = models.DecimalField(_("Delivery Price"), max_digits=11, decimal_places=2, default=0)
    order_date = models.DateTimeField(_("Order DAte"), auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.user

    #### Do post save, after create cart status change to submmited ####


def close_order_cart(sender, instance, **kwargs):
    """
    1. when the order is submited
    2. update the order.cart status to submited
    """
    cart = OrderCart.objects.get(pk=instance.cart.pk)
    cart.status = "Submitted"
    cart.save()

models.signals.post_save.connect(close_order_cart, sender=Order)

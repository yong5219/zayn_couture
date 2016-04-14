from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

from shopping.models import TimeStampedModel
from order_cart.managers import OpenCartManager, SavedCartManager


# Create your models here.
class OrderCart(TimeStampedModel):
    """
    Basket object
    """
    # Baskets can be anonymously owned - hence this field is nullable.  When a
    # anon user signs in, their two baskets are merged.
    owner = models.ForeignKey(
        User, related_name='baskets', null=True,
        verbose_name=_("Owner"))

    # Basket statuses
    # - Frozen is for when a basket is in the process of being submitted
    #   and we need to prevent any changes to it.
    OPEN, MERGED, SAVED, FROZEN, SUBMITTED = (
        "Open", "Merged", "Saved", "Frozen", "Submitted")
    STATUS_CHOICES = (
        (OPEN, _("Open - currently active")),
        (MERGED, _("Merged - superceded by another basket")),
        (SAVED, _("Saved - for items to be purchased later")),
        (FROZEN, _("Frozen - the basket cannot be modified")),
        (SUBMITTED, _("Submitted - has been ordered at the checkout")),
    )
    status = models.CharField(
        _("Status"), max_length=128, default=OPEN, choices=STATUS_CHOICES)

    # A basket can have many vouchers attached to it.  However, it is common
    # for sites to only allow one voucher per basket - this will need to be
    # enforced in the project's codebase.
    vouchers = models.ManyToManyField(
        'voucher.Voucher', verbose_name=_("Vouchers"), blank=True)

    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    date_merged = models.DateTimeField(_("Date merged"), null=True, blank=True)
    date_submitted = models.DateTimeField(_("Date submitted"), null=True,
                                          blank=True)

    # Only if a basket is in one of these statuses can it be edited
    editable_statuses = (OPEN, SAVED)

    class Meta:
        abstract = True
        app_label = 'basket'
        verbose_name = _('Basket')
        verbose_name_plural = _('Baskets')

    objects = models.Manager()
    open = OpenCartManager()
    saved = SavedCartManager()

    # def __init__(self, *args, **kwargs):
    #     super(OrderCart, self).__init__(*args, **kwargs)

    #     # We keep a cached copy of the basket lines as we refer to them often
    #     # within the same request cycle.  Also, applying offers will append
    #     # discount data to the basket lines which isn't persisted to the DB and
    #     # so we want to avoid reloading them as this would drop the discount
    #     # information.
    #     self._lines = None
    #     self.offer_applications = results.OfferApplications()

    def __str__(self):
        return _(
            u"%(status)s basket (owner: %(owner)s") \
            % {'status': self.status,
               'owner': self.owner}


class Line(TimeStampedModel):
    """
    A line of a basket (product and a quantity)

    Common approaches on ordering basket lines:
    a) First added at top. That's the history-like approach; new items are
       added to the bottom of the list. Changing quantities doesn't impact
       position.
       Oscar does this by default. It just sorts by Line.pk, which is
       guaranteed to increment after each creation.
    b) Last modified at top. That means items move to the top when you add
       another one, and new items are added to the top as well.
       Amazon mostly does this, but doesn't change the position when you
       update the quantity in the basket view.
       To get this behaviour, add a date_updated field, change
       Meta.ordering and optionally do something similar on wishlist lines.
       Order lines should already be created in the order of the basket lines,
       and are sorted by their primary key, so no changes should be necessary
       there.
    """
    cart = models.ForeignKey('basket.OrderCart', related_name='lines', verbose_name=_("Cart"))

    # This is to determine which products belong to the same line
    # We can't just use product.id as you can have customised products
    # which should be treated as separate lines.  Set as a
    # SlugField as it is included in the path for certain views.
    line_reference = models.SlugField(
        _("Line Reference"), max_length=128, db_index=True)

    product = models.ForeignKey(
        'catalogue.Product', related_name='basket_lines',
        verbose_name=_("Product"))

    # We store the stockrecord that should be used to fulfil this line.
    stockrecord = models.ForeignKey(
        'partner.StockRecord', related_name='basket_lines')

    quantity = models.PositiveIntegerField(_('Quantity'), default=1)

    # We store the unit price incl tax of the product when it is first added to
    # the basket.  This allows us to tell if a product has changed price since
    # a person first added it to their basket.
    price_excl_tax = models.DecimalField(
        _('Price excl. Tax'), decimal_places=2, max_digits=12,
        null=True)
    price_incl_tax = models.DecimalField(
        _('Price incl. Tax'), decimal_places=2, max_digits=12, null=True)

    # Track date of first addition
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super(Line, self).__init__(*args, **kwargs)
        # Instance variables used to persist discount information
        self._affected_quantity = 0

    class Meta:
        abstract = True
        app_label = 'order_cart'
        # Enforce sorting by order of creation.
        ordering = ['date_created', 'pk']
        unique_together = ("order_cart", "line_reference")
        verbose_name = _('Order Cart line')
        verbose_name_plural = _('Order Cart lines')

    def __str__(self):
        return _(
            u"Order Cart #%(basket_id)d, Product #%(product_id)d, quantity"
            u" %(quantity)d") % {'basket_id': self.cart.pk,
                                 'product_id': self.product.pk,
                                 'quantity': self.quantity}

    def save(self, *args, **kwargs):
        if not self.basket.can_be_edited:
            raise PermissionDenied(
                _("You cannot modify a %s basket") % (
                    self.basket.status.lower(),))
        return super(Line, self).save(*args, **kwargs)

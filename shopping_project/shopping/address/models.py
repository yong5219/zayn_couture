import zlib

from django.core import exceptions
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.six.moves import filter
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from django.contrib.auth.models import User


@python_2_unicode_compatible
class Address(models.Model):
    """
    Superclass address object

    This is subclassed and extended to provide models for
    user, shipping and billing addresses.
    """
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
        max_length=64, choices=TITLE_CHOICES, blank=True)
    first_name = models.CharField(_("First name"), max_length=255, blank=True)
    last_name = models.CharField(_("Last name"), max_length=255, blank=True)

    # We use quite a few lines of an address as they are often quite long and
    # it's easier to just hide the unnecessary ones than add extra ones.
    line1 = models.CharField(_("First line of address"), max_length=255)
    line2 = models.CharField(
        _("Second line of address"), max_length=255, blank=True)
    line3 = models.CharField(
        _("Third line of address"), max_length=255, blank=True)
    line4 = models.CharField(_("City"), max_length=255, blank=True)
    state = models.CharField(_("State/County"), max_length=255, blank=True)
    postcode = models.CharField(
        _("Post/Zip-code"), max_length=64, blank=True)

    #: A field only used for searching addresses - this contains all the
    #: relevant fields.  This is effectively a poor man's Solr text field.
    search_text = models.TextField(
        _("Search text - used only for searching addresses"), editable=False)

    def __str__(self):
        return self.summary

    # class Meta:
    #     abstract = True
    #     verbose_name = _('Address')
    #     verbose_name_plural = _('Addresses')

    # Saving

    def save(self, *args, **kwargs):
        self._update_search_text()
        super(Address, self).save(*args, **kwargs)

    def clean(self):
        # Strip all whitespace
        for field in ['first_name', 'last_name', 'line1', 'line2', 'line3',
                      'line4', 'state', 'postcode']:
            if self.__dict__[field]:
                self.__dict__[field] = self.__dict__[field].strip()

    def _update_search_text(self):
        search_fields = filter(
            bool, [self.first_name, self.last_name,
                   self.line1, self.line2, self.line3, self.line4,
                   self.state, self.postcode])
        self.search_text = ' '.join(search_fields)

    # Properties

    # @property
    # def city(self):
    #     # Common alias
    #     return self.line4

    @property
    def summary(self):
        """
        Returns a single string summary of the address,
        separating fields using commas.
        """
        return u", ".join(self.active_address_fields())

    @property
    def salutation(self):
        """
        Name (including title)
        """
        return self.join_fields(
            ('title', 'first_name', 'last_name'),
            separator=u" ")

    # @property
    # def name(self):
    #     return self.join_fields(('first_name', 'last_name'), separator=u" ")

    # # Helpers

    # def generate_hash(self):
    #     """
    #     Returns a hash of the address summary
    #     """
    #     # We use an upper-case version of the summary
    #     return zlib.crc32(self.summary.strip().upper().encode('UTF8'))

    def join_fields(self, fields, separator=u", "):
        """
        Join a sequence of fields using the specified separator
        """
        field_values = []
        for field in fields:
            # Title is special case
            if field == 'title':
                value = self.get_title_display()
            else:
                value = getattr(self, field)
            field_values.append(value)
        return separator.join(filter(bool, field_values))

    # def populate_alternative_model(self, address_model):
    #     """
    #     For populating an address model using the matching fields
    #     from this one.

    #     This is used to convert a user address to a shipping address
    #     as part of the checkout process.
    #     """
    #     destination_field_names = [
    #         field.name for field in address_model._meta.fields]
    #     for field_name in [field.name for field in self._meta.fields]:
    #         if field_name in destination_field_names and field_name != 'id':
    #             setattr(address_model, field_name, getattr(self, field_name))

    def active_address_fields(self, include_salutation=True):
        """
        Return the non-empty components of the address, but merging the
        title, first_name and last_name into a single line.
        """
        fields = [self.line1, self.line2, self.line3,
                  self.line4, self.state, self.postcode]
        if include_salutation:
            fields = [self.salutation] + fields
        fields = [f.strip() for f in fields if f]
        try:
            fields.append(self.state)
        except exceptions.ObjectDoesNotExist:
            pass
        return fields


class ShippingAddress(Address):
    """
    A shipping address.

    A shipping address should not be edited once the order has been placed -
    it should be read-only after that.

    NOTE:
    ShippingAddress is a model of the order app. But moving it there is tricky
    due to circular import issues that are amplified by get_model/get_class
    calls pre-Django 1.7 to register receivers. So...
    TODO: Once Django 1.6 support is dropped, move AbstractBillingAddress and
    AbstractShippingAddress to the order app, and move
    PartnerAddress to the partner app.
    """

    phone_number = models.IntegerField(
        _("Phone number"), blank=True,
        help_text=_("In case we need to call you about your order"))
    notes = models.TextField(
        blank=True, verbose_name=_('Instructions'),
        help_text=_("Tell us anything we should know when delivering "
                    "your order."))

    # class Meta:
    #     abstract = True
    #     # ShippingAddress is registered in order/models.py
    #     app_label = 'order'
    #     verbose_name = _("Shipping address")
    #     verbose_name_plural = _("Shipping addresses")

    @property
    def order(self):
        """
        Return the order linked to this shipping address
        """
        try:
            return self.order_set.all()[0]
        except IndexError:
            return None


class UserAddress(ShippingAddress):
    """
    A user's address.  A user can have many of these and together they form an
    'address book' of sorts for the user.

    We use a separate model for shipping and billing (even though there will be
    some data duplication) because we don't want shipping/billing addresses
    changed or deleted once an order has been placed.  By having a separate
    model, we allow users the ability to add/edit/delete from their address
    book without affecting orders already placed.
    """
    user = models.ForeignKey(
        User, related_name='addresses', verbose_name=_("User"))

    #: Whether this address is the default for shipping
    is_default_for_shipping = models.BooleanField(
        _("Default shipping address?"), default=False)

    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        Save a hash of the address fields
        """
        # Save a hash of the address fields so we can check whether two
        # addresses are the same to avoid saving duplicates
        # self.hash = self.generate_hash()

        # Ensure that each user only has one default shipping address
        # and billing address
        self._ensure_defaults_integrity()
        super(UserAddress, self).save(*args, **kwargs)

    def _ensure_defaults_integrity(self):
        if self.is_default_for_shipping:
            self.__class__._default_manager\
                .filter(user=self.user, is_default_for_shipping=True)\
                .update(is_default_for_shipping=False)

    # class Meta:
    #     abstract = True
    #     app_label = 'addresses'
    #     verbose_name = _("User address")
    #     verbose_name_plural = _("User addresses")
    #     ordering = ['-num_orders']
    #     unique_together = ('user', 'hash')

    # def validate_unique(self, exclude=None):
    #     super(Address, self).validate_unique(exclude)
    #     qs = self.__class__.objects.filter(
    #         user=self.user,
    #         # hash=self.generate_hash())
    #     if self.id:
    #         qs = qs.exclude(id=self.id)
    #     if qs.exists():
    #         raise exceptions.ValidationError({
    #             '__all__': [_("This address is already in your address"
    #                           " book")]})

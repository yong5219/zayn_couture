# -*- coding: utf-8 -*-

import os
import re

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import pgettext_lazy

from autoslug.fields import AutoSlugField
from mptt.models import MPTTModel, TreeForeignKey
from sorl.thumbnail.fields import ImageField
from ckeditor.fields import RichTextField
from crequest.middleware import CrequestMiddleware

from shopping.utils import slugify
from shopping.models import TimeStampedModel


class Category(MPTTModel, TimeStampedModel):
    """
    Category for Product. Need to support for multi level category.
    """
    name = models.CharField(_("Name"), max_length=100)
    slug = AutoSlugField(
        _("Slug"), populate_from='name', editable=True, unique=True, max_length=150,
        help_text=_("Used for URLs, auto-generated from name if blank")
    )
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    ordering = models.IntegerField(_("Ordering"), default=None, blank=True, null=True)
    publish_date = models.DateTimeField(_("Publish date"), default=timezone.now())
    is_active = models.BooleanField(default=True)

    class MPTTMeta:
        level_attr = 'mptt_level'
        order_insertion_by = ['name']

    class Meta:
        ordering = ['ordering']
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        model = self.__class__

        # Auto calculate ordering
        if not self.ordering and self.ordering != 0:
            try:
                last = model.objects.filter(parent=self.parent).order_by('-ordering')[0]
                self.ordering = last.ordering + 1
            except IndexError:
                # This item is first row
                self.ordering = 0

        super(model, self).save(*args, **kwargs)
        model.objects.rebuild()


class Product(TimeStampedModel):
    """
    Product
    """
    main_category = TreeForeignKey('Category')
    STANDALONE, PARENT, CHILD = 'standalone', 'parent', 'child'
    STRUCTURE_CHOICES = (
        (STANDALONE, _('Stand-alone product')),
        (PARENT, _('Parent product')),
        (CHILD, _('Child product'))
    )
    structure = models.CharField(
        _("Product structure"), max_length=10, choices=STRUCTURE_CHOICES,
        default=STANDALONE)
    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='children',
        verbose_name=_("Parent product"),
        help_text=_("Only choose a parent product if you're creating a child "
                    "product.  For example if this is a size "
                    "4 of a particular t-shirt.  Leave blank if this is a "
                    "stand-alone product (i.e. there is only one version of"
                    " this product)."))
    name = models.CharField(_("Product Name"), max_length=200, blank=True, null=True)
    slug = AutoSlugField(_('Slug'), populate_from='name', editable=True, blank=True, null=True, unique=True, db_index=True)
    short_discription = models.TextField(_("Short Discription"), max_length=100)
    quick_overview = models.TextField(_("Quick Overview"), max_length=100)
    content = RichTextField(_("Prodcut Description"))
    price = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    discount_price = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return self.get_name()

    def _clean_standalone(self):
        """
        Validates a stand-alone product
        """
        if not self.name:
            raise ValidationError(_("Your product must have a name."))
        if not self.main_category:
            raise ValidationError(_("Your product must have a product class."))
        if self.parent_id:
            raise ValidationError(_("Only child products can have a parent."))

    def _clean_child(self):
        """
        Validates a child product
        """
        if not self.parent_id:
            raise ValidationError(_("A child product needs a parent."))
        if self.parent_id and not self.parent.is_parent:
            raise ValidationError(
                _("You can only assign child products to parent products."))
        if self.main_category:
            raise ValidationError(
                _("A child product can't have a product class."))

    def _clean_parent(self):
        """
        Validates a parent product.
        """
        self._clean_standalone()

    def get_name(self):
        """
        Return a product's name or it's parent's name if it has no name
        """
        name = self.name
        if not name and self.parent_id:
            name = self.parent.name
        return name
    get_name.short_description = pgettext_lazy(u"Product name", u"name")

    def can_be_parent(self, give_reason=False):
        """
        Helps decide if a the product can be turned into a parent product.
        """
        reason = None
        if self.is_child:
            reason = _('The specified parent product is a child product.')
        is_valid = reason is None
        if give_reason:
            return is_valid, reason
        else:
            return is_valid

    def save(self, *args, **kwargs):
        if self.name == '':
            self.name = None
            if self.slug == '':
                if self.parent:
                    self.slug = self.parent.slug

        crequest = CrequestMiddleware.get_request()
        self.created_by = crequest.user

        super(Product, self).save(*args, **kwargs)

    @property
    def variety_summary(self):
        """
        Return a string of all of a product's attributes
        """
        attributes = self.product_uom.all()
        pairs = [attribute.summary() for attribute in attributes]
        return ", ".join(pairs)


class UOM(TimeStampedModel):
    """
    Product UOM
    """
    name = models.CharField(_("Product UOM"), max_length=200)
    slug = AutoSlugField(
        _("Slug"), populate_from='name', editable=True, unique=True, max_length=250,
        help_text=_("Used for URLs, auto-generated from name if blank")
    )

    def __str__(self):
        return self.name


class Variety(TimeStampedModel):
    """
    Product Variety for add many variety
    """
    uom = models.ForeignKey(UOM, related_name='uom_uom')
    product = models.ForeignKey(Product, related_name='product_uom')
    quantity = models.PositiveIntegerField(_('Quantity'), default=0)

    def __str__(self):
        return self.uom.name

    def summary(self):
        """
        Gets a string representation of both the attribute and it's value,
        used e.g in product summaries.
        """
        return u"Size: %s" % (self.uom.name)


def _generate_product_image_file_name(instance, old_filename):
    """
    Use to generate picture filename based on participant's ic.
    """
    ext = os.path.splitext(old_filename)[1].lower()
    raw_data = '%s' % instance.pk
    filename = re.sub(r'[^a-z0-9-]+', '_', raw_data).strip('_')
    return 'product_image/%s/%s%s' % (filename, filename, ext,)


class ProductImage(TimeStampedModel):
    """
    Product Image for add many image
    """
    product = models.ForeignKey(Product, related_name='product_image')
    image = ImageField(upload_to=_generate_product_image_file_name)
    image_detail = models.TextField(_("Image Detail"), max_length=255, blank=True, null=True)


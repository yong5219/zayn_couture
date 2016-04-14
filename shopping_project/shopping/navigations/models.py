from django.db import models
from django.utils.translation import ugettext_lazy as _

from shopping.models import TimeStampedModel
from autoslug.fields import AutoSlugField
from mptt.models import MPTTModel, TreeForeignKey


class NavigationMenuManager(models.Manager):
    """
    Shortcut to get data from manager.
    """
    def valid(self, **kwargs):
        return self.filter(is_active=True, parent__isnull=True, **kwargs)


class NavigationMenu(MPTTModel, TimeStampedModel):
    """
    Shopping Navigation Menu
    """
    navigation = models.CharField(_("Navigation Menu"), max_length=100)
    slug = AutoSlugField(
        _("Slug"), populate_from='navigation', editable=True, unique=True, max_length=250,
        help_text=_("Used for URLs, auto-generated from name if blank")
    )
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', default=None)
    link = models.CharField(_("Url Link"), max_length=255, blank=True, default=None)
    ordering = models.IntegerField(_("Ordering"), default=None, blank=True, null=True)
    is_active = models.BooleanField(_("is_active"), default=True)

    objects = NavigationMenuManager()

    class MPTTMeta:
        order_insertion_by = ['ordering']

    class Meta:
        ordering = ['ordering']
        verbose_name = _("Navigation Menu")
        verbose_name_plural = _("Navigation Menus")

    def __str__(self):
        return self.navigation

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
        # model.objects.rebuild()


class NavigationFooterMenuManager(models.Manager):
    """
    Shortcut to get data from manager.
    """
    def valid(self, **kwargs):
        return self.filter(is_active=True, parent__isnull=True, **kwargs)


class FooterNavigationMenu(MPTTModel, TimeStampedModel):
    """
    Shopping Navigation Menu
    """
    navigation = models.CharField(_("Navigation Menu"), max_length=100)
    slug = AutoSlugField(
        _("Slug"), populate_from='navigation', editable=True, unique=True, max_length=250,
        help_text=_("Used for URLs, auto-generated from name if blank")
    )
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', default=None)
    link = models.CharField(_("Url Link"), max_length=255, blank=True, default=None)
    ordering = models.IntegerField(_("Ordering"), default=None, blank=True, null=True)
    is_active = models.BooleanField(_("is_active"), default=True)
    open_in_new = models.BooleanField(default=False)

    objects = NavigationFooterMenuManager()

    class MPTTMeta:
        order_insertion_by = ['ordering']

    class Meta:
        ordering = ['ordering']
        verbose_name = _("Navigation Footer Menu")
        verbose_name_plural = _("Navigation Footer Menus")

    def __str__(self):
        return self.navigation

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
        # model.objects.rebuild()

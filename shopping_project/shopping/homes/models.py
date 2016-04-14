import re
import os

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from sorl.thumbnail.fields import ImageField
from autoslug.fields import AutoSlugField
from easy_thumbnails.files import get_thumbnailer

from shopping.models import TimeStampedModel


class BannerSliderManager(models.Manager):
    """
    Shortcut to get data from manager.
    """
    def valid(self, **kwargs):
        return self.filter(is_active=True, **kwargs)


def _generate_slider_image_file_name(instance, old_filename):
    """
    Use to generate picture filename based on participant's ic.
    """
    ext = os.path.splitext(old_filename)[1].lower()
    raw_data = '%s' % instance.pk
    filename = re.sub(r'[^a-z0-9-]+', '_', raw_data).strip('_')
    return 'slider_image/%s/%s%s' % (filename, filename, ext,)


class BannerSlider(TimeStampedModel):
    """
    shopping Banner Slider
    """
    title = models.CharField(_("Title"), max_length=200)
    slug = AutoSlugField(
        _("Slug"), populate_from='name', editable=True, unique=True, max_length=250,
        help_text=_("Used for URLs, auto-generated from name if blank")
    )
    banner_image = ImageField(upload_to=_generate_slider_image_file_name)
    url_link = models.URLField(_("Link"), max_length=255, blank=True, null=True)
    ordering = models.IntegerField(_("Ordering"), default=None, blank=True, null=True)
    is_active = models.BooleanField(_("is_active"), default=True)
    open_in_new = models.BooleanField(default=True)

    objects = BannerSliderManager()

    class Meta:
        ordering = ['ordering']
        verbose_name = _("Banner Slider")
        verbose_name_plural = _("Banner Sliders")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        model = self.__class__

        # Auto calculate ordering
        if not self.ordering and self.ordering != 0:
            try:
                last = model.objects.order_by('-ordering')[0]
                self.ordering = last.ordering + 1
            except IndexError:
                # This item is first row
                self.ordering = 0

        super(model, self).save(*args, **kwargs)

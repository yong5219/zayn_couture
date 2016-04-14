from django.db import models
from django.contrib.auth.models import User


# class FancyboxMedia:
#     css = {
#         "all": (
#             "js/fancybox/jquery.fancybox.css",
#         )
#     }
#     js = (
#         "js/jquery-1.11.2.min.js",
#         "js/jquery.mousewheel-3.0.6.pack.js",
#         "js/fancybox/jquery.fancybox.pack.js",
#         "js/admin.fancybox.js",
#     )


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self updating
    ``created`` and ``modified`` fields.
    """
    created_by = models.ForeignKey(
        User, blank=True, null=True, related_name="%(app_label)s_%(class)s_created_user",
        editable=False
    )
    modified_by = models.ForeignKey(
        User, blank=True, null=True, related_name="%(app_label)s_%(class)s_modified_user",
        editable=False
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

from django import template

from products.models import Category

register = template.Library()


@register.assignment_tag(takes_context=True)
def get_product_category(context):
    return Category.objects.all()

from django import template

from navigations.models import NavigationMenu, FooterNavigationMenu

register = template.Library()


@register.assignment_tag(takes_context=True)
def get_navigations_menu(context):
    return NavigationMenu.objects.valid()


@register.assignment_tag(takes_context=True)
def get_navigations_footer_menu(context):
    return FooterNavigationMenu.objects.valid()

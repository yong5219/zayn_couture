from django import template

register = template.Library()


@register.filter
def field_type(field, ftype):
    try:
        t = field.field.widget.__class__.__name__
        return t.lower() == ftype
    except:
        pass

    return False


@register.filter
def add_class(field, css):
    if field.field.widget.attrs.get('class'):
        default_class = field.field.widget.attrs.get('class').split(" ")
        addon_class = css.split(" ")
        combined_class = default_class + list(set(addon_class) - set(default_class))
        field.field.widget.attrs['class'] = " ".join(combined_class)
    else:
        field.field.widget.attrs['class'] = css
    return field.as_widget()


@register.filter
def is_voted(article, user):
    if user:
        return article.is_voted(user)
    else:
        return False


@register.filter
def get_result(article, user):
    return article.get_user_result(user)

from django import forms
from django.utils.translation import ugettext_lazy as _

from order_cart import widgets


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(initial=1, min_value=1, label=_('Quantity'))

    def __init__(self, cart, product, *args, **kwargs):
        # Note, the product passed in here isn't necessarily the product being
        # added to the cart. For child products, it is the *parent* product
        # that gets passed to the form. An optional product_id param is passed
        # to indicate the ID of the child product being added to the cart.
        self.cart = cart
        self.parent_product = product

        super(AddToCartForm, self).__init__(*args, **kwargs)

        # Dynamically build fields
        if product.is_parent:
            self._create_parent_product_fields(product)
        self._create_product_fields(product)

    # Dynamic form building methods

    def _create_parent_product_fields(self, product):
        """
        Adds the fields for a "group"-type product (eg, a parent product with a
        list of children.

        Currently requires that a stock record exists for the children
        """
        choices = []
        disabled_values = []
        for child in product.children.all():
            # Build a description of the child, including any pertinent
            # attributes
            attr_summary = child.attribute_summary
            if attr_summary:
                summary = attr_summary
            else:
                summary = child.get_title()

            # Check if it is available to buy
            info = self.cart.strategy.fetch_for_product(child)
            if not info.availability.is_available_to_buy:
                disabled_values.append(child.id)

            choices.append((child.id, summary))

        self.fields['child_id'] = forms.ChoiceField(
            choices=tuple(choices), label=_("Variant"),
            widget=widgets.AdvancedSelect(disabled_values=disabled_values))

    def _create_product_fields(self, product):
        """
        Add the product option fields.
        """
        for option in product.options:
            self._add_option_field(product, option)

from django import forms


from orders.models import Order


class CheckOutForm(forms.ModelForm):
    cart = forms.CharField(widget=forms.HiddenInput())
    user = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Order
        exclude = ['price', 'delivery_price', 'order_date', 'is_paid', 'is_delivered']
        fields = ['title', 'first_name', 'last_name', 'contact_no', 'line1', 'line2', 'line3', 'line4', 'state', 'postcode', 'remark']

    def save(self, force_insert=False, force_update=False, commit=True, user=None, cart=None):
        m = super(CheckOutForm, self).save(commit=False)
        if commit:
            if user:
                m.user = user
                m.cart = cart
            m.save()
        return m

    # def clean_order(self):
    #     try:
    #         order = Order.objects.get(pk=self.cleaned_data['order'])
    #     except:
    #         raise forms.ValidationError('Order does not exist.')
    #     else:
    #         return order

    # def send_complaint_email(self):
    #     site = Site.objects.get_current()
    #     context = {
    #         'user': self.user,
    #         'protocol': get_protocol(),
    #         'site': site,
    #     }

    #     mail.send(
    #         [self.user.email, ],
    #         settings.DEFAULT_FROM_EMAIL,
    #         template='notification/notification_email',
    #         context=context,
    #         priority=PRIORITY.medium,
    #     )

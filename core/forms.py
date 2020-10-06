from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'Paypal')
)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '1234 Main St', 'class': 'form-control'}), required=False)
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Apartment or suite', 'class': 'form-control'}))
    country = CountryField(blank_label='(Select Country)').formfield(
        widget=CountrySelectWidget(attrs={'class': 'custom-select d-block w-100'}), required=False)
    zip = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}), required=False)
    save_address = forms.BooleanField(required=False, widget=forms.CheckboxInput(
        attrs={'class': 'custom-control-input'}))
    use_default = forms.BooleanField(required=False, widget=forms.CheckboxInput(
        attrs={'class': 'custom-control-input'}))
    payment_method = forms.ChoiceField(
        widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Promo Code', 'class': 'form-control'}))


class RefundForm(forms.Form):
    order_id = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Your Order ID'}))
    message = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Describe your issue briefly...', 'rows': '4'}))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'placeholder': 'Your contact Email.'}))

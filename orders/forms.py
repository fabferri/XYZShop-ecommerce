from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']


class PaymentForm(forms.Form):
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect,
        initial='card'
    )
    card_number = forms.CharField(
        max_length=16,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '1234 5678 9012 3456', 'class': 'payment-input'})
    )
    card_holder = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'John Doe', 'class': 'payment-input'})
    )
    expiry_date = forms.CharField(
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'MM/YY', 'class': 'payment-input'})
    )
    cvv = forms.CharField(
        max_length=4,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '123', 'class': 'payment-input', 'type': 'password'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        if payment_method == 'card':
            if not cleaned_data.get('card_number'):
                raise forms.ValidationError('Card number is required for card payments')
            if not cleaned_data.get('card_holder'):
                raise forms.ValidationError('Card holder name is required')
            if not cleaned_data.get('expiry_date'):
                raise forms.ValidationError('Expiry date is required')
            if not cleaned_data.get('cvv'):
                raise forms.ValidationError('CVV is required')
        
        return cleaned_data

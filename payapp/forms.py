from django import forms

class PaymentForm(forms.Form):
    recipient_email = forms.EmailField(required=True, label="Recipient's Email")
    amount = forms.DecimalField(min_value=0.01, decimal_places=2, required=True)
    
class RequestForm(forms.Form):
    sender_email = forms.EmailField(required=True, label="Sender's Email")
    amount = forms.DecimalField(min_value=0.01, decimal_places=2, required=True) 
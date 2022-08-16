from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user','numero_vendedor','nombre_vendedor','order_number','first_name', 'last_name', 'phone', 'email','order_total','ip']


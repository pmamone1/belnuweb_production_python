from django import forms
from store.models import Product, Variation,ReviewRating


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'description','price','recargo_interior','porcentaje_vv', 'category', 'images']
    
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject','review','rating']

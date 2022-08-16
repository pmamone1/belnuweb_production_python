from rest_framework import serializers
from .models import Product, Variation


class VariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variation
        fields = ('product','subtitulo', 'variation_value', 'stock','image', 'is_active')
        

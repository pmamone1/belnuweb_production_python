from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Variation, Product
from .serializers import VariationSerializer



class VariationApiView(APIView):
    
    def get(self, request):
        
        variations = Variation.objects.all()
        serializer = VariationSerializer(variations)
        print(serializer.data)
        return Response(serializer.data)

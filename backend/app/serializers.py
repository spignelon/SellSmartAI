from rest_framework import serializers
from .models import ConnectedSocialMedia, ProductListings

class ConnectedSocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectedSocialMedia
        fields = '__all__'

class ProductListingsSerializer(serializers.ModelSerializer):
    # Handle the price as a string in the serializer
    price = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductListings
        fields = '__all__'
    
    def get_price(self, obj):
        # Return the price as is without trying to convert
        return obj.price
from rest_framework import serializers
from app.models import ConnectedSocialMedia, ProductListings 

class ConnectedSocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectedSocialMedia
        fields = ['id', 'instagram_link', 'facebook_link', 'tiktok_link']

class ProductListingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductListings
        fields = ['product_id', 'created_at', 'images_list', 'product_title', 'price', 'product_details', 'about_this_item', 'product_description', 'updated_at', 'approved']
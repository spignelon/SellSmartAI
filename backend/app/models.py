from django.db import models
from django.conf import settings

# Create your models here.
class ConnectedSocialMedia(models.Model):
    instagram_link = models.CharField(max_length=100)
    facebook_link = models.CharField(max_length=100)
    tiktok_link = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class ProductListings(models.Model):
    product_id = models.CharField(max_length=255, primary_key=True)
    images_list = models.JSONField()
    product_title = models.CharField(max_length=255)
    price = models.CharField(max_length=50, null=True)  # Changed from FloatField to CharField
    product_details = models.JSONField(null=True)
    about_this_item = models.JSONField(null=True)
    product_description = models.TextField(null=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_full_image_urls(self):
        """
        Convert image paths to full URLs for frontend use
        """
        if not self.images_list:
            return []
            
        full_urls = []
        for img_path in self.images_list:
            if img_path.startswith('http'):
                full_urls.append(img_path)
            elif img_path.startswith('/static/'):
                # For development, add the full URL if not already present
                if settings.DEBUG:
                    full_urls.append(f"http://127.0.0.1:8000{img_path}")
                else:
                    full_urls.append(img_path)
            else:
                full_urls.append(f"{settings.STATIC_URL}{img_path}")
                
        return full_urls

    def __str__(self):
        return self.product_title
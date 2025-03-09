from django.db import models

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
    product_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    images_list = models.JSONField()
    product_title = models.CharField(max_length=100)
    price = models.CharField(max_length=100)
    product_details = models.JSONField()
    about_this_item = models.TextField()
    product_description = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)
    def __str__(self):
        return self.product_title
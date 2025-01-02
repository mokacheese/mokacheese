from django.db import models
from .get_lat_lng import get_lat_lng
from django.conf import settings

# Create your models here.

class Recommend(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    rating = models.FloatField(default=0.0)
    file = models.FileField(upload_to='media/documents/', blank=True, null=True)
    restaurant_name = models.CharField(max_length=100, default=None, null=True)
    r_address = models.CharField(max_length=100)
    r_latitude = models.FloatField(null=True, blank=True)
    r_longitude = models.FloatField(null=True, blank=True)
    my_address = models.CharField(max_length=100, default=None, null=True)
    my_latitude = models.FloatField(default=None, null=True, blank=True)
    my_longitude = models.FloatField(default=None, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.r_latitude or not self.r_longitude:
            self.r_latitude, self.r_longitude = get_lat_lng(self.r_address)
        super().save(*args, **kwargs)


    def __str__(self):
        return self.title
    
class Restaurant(models.Model):
    r_name = models.CharField(max_length=100)
    r_desc = models.TextField()
    r_desc_summary = models.TextField()
    phone_number = models.CharField(max_length=30)
    address = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    seats = models.CharField(max_length=30)
    parking = models.CharField(max_length=30)
    closed_days = models.CharField(max_length=30)
    classification = models.CharField(max_length=30)

    def save(self, *args, **kwargs):
        if not self.latitude or not self.longitude:
            self.latitude, self.longitude = get_lat_lng(self.address)
        super().save(*args, **kwargs)

class RecommendComment(models.Model):
    info = models.ForeignKey(Recommend, related_name='recommend_comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    comment_rating = models.IntegerField(default=0)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content

class RestaurantComment(models.Model):
    info = models.ForeignKey(Restaurant, related_name='restaurant_comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    comment_rating = models.IntegerField(default=0)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=200)

    def __str__(self):
        return self.user.username

class Item(models.Model):
    User = models.ForeignKey(User,null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200, null=True, blank=True)
    location = models.CharField(max_length=200)
    starting_bid = models.FloatField()
    lat = models.FloatField()
    lng = models.FloatField()
    image = models.ImageField(null=True, blank = True)
    bidding = models.BooleanField(default=True)
    buyNow = models.FloatField()
    created_at = models.DateField(auto_now_add=True)
    bidding_end_data = models.DateField(default=now)

    def __str__(self):
        return self.title

class ItemStatus(models.Model):
    user = models.ForeignKey(User,null=True, on_delete=models.SET_NULL)
    item = models.OneToOneField(Item, null=True, on_delete=models.SET_NULL)
    bid = models.FloatField()
    sold = models.BooleanField(default=False)

    def __str__(self):
        return self.item.title

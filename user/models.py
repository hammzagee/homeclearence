from django.db import models
from django.contrib.auth.models import User

# Create your models here.

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

    def __str__(self):
        return self.title

class ItemStatus(models.Model):
    user = models.ForeignKey(User,null=True, on_delete=models.SET_NULL)
    item = models.OneToOneField(Item, null=True, on_delete=models.SET_NULL)
    bid = models.FloatField()
    sold = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.item.title

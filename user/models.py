from django.db import models

# Create your models here.


class Item(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200, null=True, blank=True)
    location = models.CharField(max_length=200)
    starting_bid = models.FloatField()
    lat = models.FloatField()
    lng = models.FloatField()
    image = models.ImageField(null=True, blank = True)
    current_bid = models.FloatField()
    sold = models.BooleanField()
    bidding = models.BooleanField()
    buyNow = models.FloatField()

    def __str__(self):
        return self.title

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.base import Model
from django.db.models.fields import BooleanField, CharField, DateTimeField, DecimalField, TextField, URLField
from django.db.models.fields.related import OneToOneField


class User(AbstractUser):
    pass


class Category(models.Model):
    name = CharField(max_length=64)

    def __str__(self) -> str:
        return f"{self.name}"


class AuctionListing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    timestamp = DateTimeField(auto_now_add=True, editable=False)
    title = CharField(max_length=64)
    description = TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, blank=True, null=True, related_name="listings")
    image_url = URLField(blank=True)
    starting_bid_value = DecimalField(max_digits=6, decimal_places=2)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, editable=False, default=None ,related_name="wins")
    is_active = BooleanField(default=True)
    users_in_watchlist = models.ManyToManyField(User, blank=True, related_name="watchlist")

    def __str__(self) -> str:
        return f"{self.title} ({self.user})"


class Bid(models.Model):
    #TODO: ver qué pasa si elimino el usuario, quién gana la subasta
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    value = DecimalField(max_digits=6, decimal_places=2)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self) -> str:
        return f"{self.value}"

class Comment(models.Model):
    timestamp = DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment = TextField(max_length=200)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")

    def __str__(self) -> str:
        return f"{self.comment[:50]}..."
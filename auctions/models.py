from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.base import Model
from django.db.models.fields import BooleanField, CharField, DateTimeField, DecimalField, TextField, URLField
from django.db.models.fields.related import OneToOneField


class User(AbstractUser):
    watchlist = models.ManyToManyField('AuctionListing', blank=True, related_name="users_in_watchlist")


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
    image_url = URLField(blank=True, null=True, default="../static/auctions/no-image-available.jpg")
    starting_bid_value = DecimalField(max_digits=6, decimal_places=2)
    is_active = BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.title} ({self.user})"
    
    @property
    def current_bid(self):
        return self.bids.order_by("-value").first()


class Bid(models.Model):
    #TODO: ver qué pasa si elimino el usuario, quién gana la subasta
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    value = DecimalField(max_digits=6, decimal_places=2)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self) -> str:
        return f"[{self.listing.title}] {self.value} ({self.user})"

class Comment(models.Model):
    timestamp = DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment = TextField(max_length=200)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")

    def __str__(self) -> str:
        return f"{self.comment[:50]}..."
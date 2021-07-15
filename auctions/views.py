from django import forms

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models.fields import CharField, DecimalField, TextField, URLField
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Category, User, AuctionListing

class NewListingForm(forms.Form):
    title = forms.CharField(max_length=64, label="Title")
    description = forms.CharField(widget=forms.Textarea, label="Description")
    starting_bid_value = forms.DecimalField(max_digits=6, decimal_places=2, label="Starting Bid value", max_value=9999.99)
    image_url = forms.URLField(required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all().order_by("name"), required=False, label="Category")


def index(request):
    return render(request, "auctions/index.html", {
        "auction_listings": AuctionListing.objects.filter(is_active=True).order_by("-timestamp"),
        "users": User.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required()
def create_listing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid_value = form.cleaned_data["starting_bid_value"]
            image_url = form.cleaned_data["image_url"]
            category = form.cleaned_data["category"]
            try:
                if request.user.is_authenticated:
                    user = request.user
                    listing = AuctionListing(
                        user = user, 
                        title = title, 
                        description = description,
                        category = category,
                        image_url = image_url,
                        starting_bid_value = starting_bid_value
                        )
                    listing.save()
                    return HttpResponseRedirect(reverse("index"))
            except:
                return render(request, "auctions/new_listing.html", {
                "message": "There was an error creating your new listing.",
                "form": form
            })
        else:
            return render(request, "auctions/new_listing.html", {
                    "message": "There was an error creating your new listing.",
                    "form": form
                })
    else:
        return render(request, "auctions/new_listing.html", {
            "form": NewListingForm()
        })

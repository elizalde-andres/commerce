from django import forms

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models.fields import CharField, DecimalField, TextField, URLField
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, AuctionListing, Bid, Comment  

class NewListingForm(forms.Form):
    title = forms.CharField(max_length=64, label="Title")
    description = forms.CharField(widget=forms.Textarea, label="Description")
    starting_bid_value = forms.DecimalField(max_digits=6, decimal_places=2, label="Starting Bid value", max_value=9999.99)
    image_url = forms.URLField(required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all().order_by("name"), required=False, label="Category")


def index(request):
    return render(request, "auctions/index.html", {
        "auction_listings": AuctionListing.objects.filter(is_active=True).order_by("-timestamp")
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
            try:
                if request.user.is_authenticated:
                    user = request.user

                    # Create listing
                    listing = AuctionListing(
                        user = user, 
                        title = form.cleaned_data["title"], 
                        description = form.cleaned_data["description"],
                        category = form.cleaned_data["category"],
                        starting_bid_value = form.cleaned_data["starting_bid_value"]
                        )
                    image_url = form.cleaned_data["image_url"]
                    if (image_url):
                        listing.image_url = image_url
                    # Save to database 
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


def listing(request, id):
    exception = False
    message = ""
    if request.method == "POST":
        try:
            listing = AuctionListing.objects.get(pk=id)
            if request.user.is_authenticated:
                user = request.user

                # Check which action was taken in listing page
                # Update bid
                if request.POST.get("bid"):
                    try:
                        bid_value = float(request.POST.get("bid"))
                    except ValueError:
                        return render(request, "auctions/listing.html", {
                            "message": "You can't place a bid on your own listing",
                            "listing": listing
                        })
                    if listing.current_bid:
                        current_bid = listing.current_bid.value
                    else:
                        current_bid = listing.starting_bid_value

                    if listing.user == user:
                        return render(request, "auctions/listing.html", {
                            "message": "You can't place a bid on your own listing",
                            "listing": listing
                        })
                    elif bid_value <= current_bid or bid_value > 999999:
                        return render(request, "auctions/listing.html", {
                            "message": f"The bid must be greater than { current_bid } and smaller than 1 million",
                            "listing": listing
                        })
                    else: 
                        bid = Bid(user = user, 
                                value = bid_value, 
                                listing = listing)
                        bid.save()
                        return render(request, "auctions/listing.html", {
                            "message": "Your bid was successful.",
                            "listing": listing
                        })   

                # Add/Remove listing from watchlist
                elif request.POST.get("watchlist"):
                    watchlist = user.watchlist.filter(pk=id)
                    if watchlist:
                        user.watchlist.remove(listing)
                    else:
                        user.watchlist.add(listing)
                    return render(request, "auctions/listing.html", {
                        "listing": listing
                    })

                # Close auction 
                elif request.POST.get("close"):
                    listing.is_active = False
                    listing.save()
                    return render(request, "auctions/listing.html", {
                            "message": "Your auction was closed successfuly...",
                            "listing": listing
                        })

                # Add a comment
                elif request.POST.get("comment"):
                    comment = Comment(user = user,
                                comment = request.POST.get("comment"),
                                listing = listing)
                    comment.save()
                    return render(request, "auctions/listing.html", {
                            "listing": listing
                        })
            else:
                return HttpResponseRedirect(reverse("login"))
        except:
            exception = True
            message = "Sorry. Something went wrong while processing your request."
    if (request.method == "GET" or exception):
        try:
            listing = AuctionListing.objects.get(pk=id)
            return render(request, "auctions/listing.html", {
                        "listing": listing,
                        "message": message
            })
        except:
            return render(request, "auctions/404.html", {
                    "message": "The listing you are trying to reach does not exist."
                })

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all().order_by("name")
    })


def category(request, category):
    try:
        if category != "Uncategorized":
            return render(request, "auctions/category.html", {
                "auction_listings": Category.objects.get(name=category).listings.all().order_by("-timestamp"),
                "category": category
            })
        else:
            return render(request, "auctions/category.html", {
                "auction_listings": AuctionListing.objects.all().filter(category=None).order_by("-timestamp"),
                "category": category
            })
    except:
        return render(request, "auctions/404.html", {
                    "message": "The category you are trying to reach does not exist."
                })



@login_required()
def watchlist(request):
    user = request.user
    if user.is_authenticated:
        return render(request, "auctions/watchlist.html", {
            "auction_listings": user.watchlist.all().order_by("-timestamp")
        })
    else:
        return HttpResponseRedirect(reverse("login"))
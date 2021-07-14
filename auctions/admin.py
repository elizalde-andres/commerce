from django.contrib import admin
from .models import *

# Register your models here.

class AuctionListingAdmin(admin.ModelAdmin):
    filter_horizontal = ("users_in_watchlist", )

admin.site.register(User)
admin.site.register(Category)
admin.site.register(AuctionListing, AuctionListingAdmin)
admin.site.register(Bid)
admin.site.register(Comment)
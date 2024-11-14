from django.contrib import admin
from .models import User, Ticket, Show, Movie, Food, Transaction, TheatreAdmin, Theatre, Wallet, Screen
# Register your models here.

admin.site.register(User)
admin.site.register(Ticket)
admin.site.register(Show)
admin.site.register(Movie)
admin.site.register(Food)
admin.site.register(Transaction)
admin.site.register(TheatreAdmin)
admin.site.register(Theatre)
admin.site.register(Wallet)
admin.site.register(Screen)

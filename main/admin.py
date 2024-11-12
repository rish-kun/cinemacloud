from django.contrib import admin
from .models import User, Ticket, Show, Movie, Food, Transaction, TheatreAdmin

admin.site.register(User)
admin.site.register(Ticket)
admin.site.register(Show)
admin.site.register(Movie)
admin.site.register(Food)
admin.site.register(Transaction)
admin.site.register(TheatreAdmin)

from django.contrib import admin
from .models import Book, Favourite, Genre

admin.site.register(Book)
admin.site.register(Favourite)
admin.site.register(Genre)
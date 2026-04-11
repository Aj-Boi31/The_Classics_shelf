from django.contrib import admin
from .models import Book, Favourite, Genre

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'year_published', 'genre']
    list_filter = ['genre']
    search_fields = ['title', 'author']
    ordering = ['title']

@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'added_on']
    list_filter = ['user']
    search_fields = ['user__username', 'book__title']
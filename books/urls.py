from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookListView.as_view(), name='book_list'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('book/add/', views.BookCreateView.as_view(), name='book_add'),
    path('book/<int:pk>/favourite/', views.favourite_toggle, name='favourite_toggle'),
    path('favourites/', views.FavouriteListView.as_view(), name='favourites'),
    path('contact/', views.contact_view, name='contact'),
]
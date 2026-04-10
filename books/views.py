from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Book, Favourite
from .forms import ContactForm

class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'

class BookDetailView(DetailView):
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_favourite'] = Favourite.objects.filter(
                user=self.request.user,
                book=self.object
            ).exists()
        else:
            context['is_favourite'] = False
        return context

class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    template_name = 'books/book_form.html'
    fields = ['title', 'author', 'year_published', 'genre', 'description', 'cover_image']
    success_url = reverse_lazy('book_list')

@login_required
def favourite_toggle(request, pk):
    book = get_object_or_404(Book, pk=pk)
    favourite = Favourite.objects.filter(user=request.user, book=book)
    if favourite.exists():
        favourite.delete()
        messages.success(request, f'Removed "{book.title}" from your favourites.')
    else:
        Favourite.objects.create(user=request.user, book=book)
        messages.success(request, f'Added "{book.title}" to your favourites!')
    return redirect('book_detail', pk=pk)

class FavouriteListView(LoginRequiredMixin, ListView):
    model = Favourite
    template_name = 'books/favourites.html'
    context_object_name = 'favourites'

    def get_queryset(self):
        return Favourite.objects.filter(user=self.request.user)


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Your message has been sent. Thank you!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'books/contact.html', {'form': form})
from django.shortcuts import get_object_or_404, render

from book.models import Book
from genres.models import Genres


def home(request, genre_slug=None):
    data = Book.objects.all()
    selected_genre = None
    if genre_slug is not None:
        selected_genre = get_object_or_404(Genres, slug=genre_slug)
        data = Book.objects.filter(genres=selected_genre)
    genres = Genres.objects.all()
    return render(request, 'home.html', {'data': data, 'genre': genres, 'selected_genre': selected_genre})

from django.shortcuts import render
from book.models import Book
from genres.models import Genres
def home(request, genre_slug = None):
    data = Book.objects.all()
    if genre_slug is not None:
        genres = Genres.objects.get(slug = genre_slug)
        data = Book.objects.filter(genres = genres)
    genres = Genres.objects.all()
    return render(request, 'home.html', {'data' : data, 'genre' : genres})
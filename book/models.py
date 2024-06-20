from django.db import models
from genres.models import Genres
from django.contrib.auth.models import User
# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    author = models.CharField(max_length=255)
    description = models.TextField()
    genres = models.ManyToManyField(Genres, related_name="genres")
    quantity = models.IntegerField()
    image = models.ImageField(upload_to='book/media/images/')
    buyers = models.ManyToManyField(User, blank=True)
    
    def __str__(self):
        return self.title
    
    
class Review(models.Model):
    post = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=30)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reviewd by {self.name}"
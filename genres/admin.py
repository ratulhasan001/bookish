from django.contrib import admin
from .models import Genres

class GenresAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('name',)}
    list_display = ['name', 'slug']

admin.site.register(Genres, GenresAdmin)
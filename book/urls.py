from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('details/<int:id>/', views.DetailBookView.as_view(), name='book_details'),
    path("buy_car/<int:id>/", views.update_quantity , name="borrow_book"),
]
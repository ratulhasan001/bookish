from django.shortcuts import render, redirect, get_object_or_404
from . import models
from . import forms
from book.models import Book
from accounts.models import UserAccount
from django.views.generic import CreateView,UpdateView,DeleteView,DetailView
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib import messages
# Create your views here.

class DetailBookView(DetailView):
    model = models.Book
    pk_url_kwarg = 'id'
    template_name = 'book_details.html'
    def post(self, request, *args, **kwargs):
        review_form = forms.ReviewForm(data=self.request.POST)
        post = self.get_object()
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.post = post
            new_review.name = request.user.username 
            new_review.email = request.user.email 
            new_review.save()
        return self.get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        reviews = post.reviews.all()
        ReviewForm = forms.ReviewForm()
        user_has_borrowed = False
        if self.request.user.is_authenticated:
            user_has_borrowed = post.buyers.filter(id=self.request.user.id).exists()
        context['reviews'] = reviews
        context['ReviewForm'] = ReviewForm
        context['user_has_borrowed'] = user_has_borrowed
        return context

def send_transaction_email(user, title, subject, template):
        message = render_to_string(template, {
            'user' : user,
            'title' : title,
        })
        send_email = EmailMultiAlternatives(subject, '', to=[user.email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()

def update_quantity(request, id):
    book = Book.objects.get(pk=id)
    book.quantity -= 1
    book.buyers.add(request.user)
    book.save()
    user_account = UserAccount.objects.get(user=request.user)
    user_account.balance -= book.price
    user_account.save()
    
    send_transaction_email(request.user, book.title, "Borrow Message", "borrow_email.html")
    return redirect("homepage")

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.views.generic import DetailView

from accounts.models import UserAccount
from transcations.constants import BORROW
from transcations.models import Transaction

from . import forms
from .models import Book


class DetailBookView(DetailView):
    model = Book
    pk_url_kwarg = 'id'
    template_name = 'book_details.html'

    def post(self, request, *args, **kwargs):
        book = self.get_object()
        if not request.user.is_authenticated:
            return redirect('user_login')
        if not book.buyers.filter(pk=request.user.pk).exists():
            messages.error(request, 'Only readers who have borrowed this book can review it.')
            return redirect('book_details', id=book.id)

        review_form = forms.ReviewForm(data=request.POST)
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.post = book
            new_review.name = request.user.username
            new_review.email = request.user.email
            new_review.save()
            messages.success(request, 'Thanks for your review!')
            return redirect('book_details', id=book.id)

        self.object = book
        context = self.get_context_data(object=book)
        context['ReviewForm'] = review_form
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.object
        user_has_borrowed = False
        if self.request.user.is_authenticated:
            user_has_borrowed = book.buyers.filter(id=self.request.user.id).exists()
        context['reviews'] = book.reviews.order_by('-created_on')
        context['ReviewForm'] = forms.ReviewForm()
        context['user_has_borrowed'] = user_has_borrowed
        return context


def send_transaction_email(user, title, subject, template):
    message = render_to_string(template, {
        'user': user,
        'title': title,
    })
    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()


@login_required
@require_POST
def update_quantity(request, id):
    """Borrow a book: pay its price from the user's balance."""
    book = get_object_or_404(Book, pk=id)

    with transaction.atomic():
        book = Book.objects.select_for_update().get(pk=book.pk)
        account, _ = UserAccount.objects.select_for_update().get_or_create(user=request.user)

        if book.buyers.filter(pk=request.user.pk).exists():
            messages.error(request, 'You have already borrowed this book. Return it before borrowing it again.')
            return redirect('book_details', id=book.id)
        if book.quantity < 1:
            messages.error(request, 'Sorry, this book is out of stock.')
            return redirect('book_details', id=book.id)
        if account.balance < book.price:
            messages.error(
                request,
                f'Insufficient balance. This book costs {book.price}$ and you have {account.balance}$.'
            )
            return redirect('book_details', id=book.id)

        book.quantity -= 1
        book.save(update_fields=['quantity'])
        book.buyers.add(request.user)
        account.balance -= book.price
        account.save(update_fields=['balance'])
        Transaction.objects.create(
            user=account, account=account, amount=book.price,
            balance_after_transaction=account.balance, transaction_type=BORROW,
        )

    send_transaction_email(request.user, book.title, "Borrow Message", "borrow_email.html")
    messages.success(request, f'You borrowed "{book.title}". {book.price}$ was deducted from your balance.')
    return redirect('book_details', id=book.id)

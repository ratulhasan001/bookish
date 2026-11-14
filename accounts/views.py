from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from accounts.models import UserAccount
from book.models import Book
from transcations.constants import RETURN
from transcations.models import Transaction

from . import forms


class UserLoginView(LoginView):
    template_name = 'register.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy('homepage')

    def form_valid(self, form):
        messages.success(self.request, 'Logged in successfully')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'Login'
        return context


def register(request):
    if request.method == 'POST':
        register_form = forms.RegistrationForm(request.POST)
        if register_form.is_valid():
            register_form.save()
            messages.success(request, 'Account created successfully. You can log in now.')
            return redirect('user_login')
    else:
        register_form = forms.RegistrationForm()
    return render(request, 'register.html', {'form': register_form, 'type': 'Register'})


@require_POST
def user_logout(request):
    # Logout is POST-only (as required by Django 5's LogoutView).
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('user_login')


@login_required
def profile(request):
    UserAccount.objects.get_or_create(user=request.user)
    data = Book.objects.filter(buyers=request.user)
    return render(request, "profile.html", {'data': data})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        profile_form = forms.ChangeUserForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile Updated Successfully')
            return redirect('profile')
    else:
        profile_form = forms.ChangeUserForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': profile_form})


@login_required
def pass_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password Updated Successfully')
            update_session_auth_hash(request, form.user)
            return redirect('profile')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'pass_change.html', {'form': form})


@login_required
@require_POST
def return_book(request, id):
    """Return a borrowed book and refund its price."""
    book = get_object_or_404(Book, pk=id)

    with transaction.atomic():
        book = Book.objects.select_for_update().get(pk=book.pk)
        if not book.buyers.filter(pk=request.user.pk).exists():
            messages.error(request, 'You have not borrowed this book.')
            return redirect('profile')

        user_account, _ = UserAccount.objects.select_for_update().get_or_create(user=request.user)
        book.buyers.remove(request.user)
        book.quantity += 1
        book.save(update_fields=['quantity'])
        user_account.balance += book.price
        user_account.save(update_fields=['balance'])
        Transaction.objects.create(
            user=user_account, account=user_account, amount=book.price,
            balance_after_transaction=user_account.balance, transaction_type=RETURN,
        )

    messages.success(request, f'You returned "{book.title}". {book.price}$ was refunded.')
    return redirect('profile')

from django.shortcuts import render, redirect, get_object_or_404
from . import forms
from django.contrib.auth.forms import  AuthenticationForm, PasswordChangeForm
from django.contrib.auth import authenticate, login , update_session_auth_hash, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from book.models import Book
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.conf import settings
from accounts.models import UserAccount

class UserLoginView(LoginView):
    template_name = 'register.html'
    def get_success_url(self):
        return reverse_lazy('homepage')
    def form_valid(self, form):
        messages.success(self.request, 'Logged in Successful')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.success(self.request, 'Logged in information incorrect')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'Login'
        return context
    
def register(request):
    if request.method == 'POST':
        register_form = forms.RegistrationForm(request.POST)
        if register_form.is_valid():
            register_form.save()
            messages.success(request, 'Account Created Successfully')
            return redirect('register')
    
    else:
        register_form = forms.RegistrationForm()
    return render(request, 'register.html', {'form' : register_form, 'type' : 'Register'})

def user_logout(request):
    logout(request)
    return redirect('user_login')



@login_required
def profile(request):
    data = Book.objects.filter(buyers=request.user)
    return render(request, "profile.html", {'data': data})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        profile_form = forms.ChangeUserForm(request.POST, instance = request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile Updated Successfully')
            return redirect('profile')
    
    else:
        profile_form = forms.ChangeUserForm(instance = request.user)
    return render(request, 'edit_profile.html', {'form' : profile_form})

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
    return render(request, 'pass_change.html', {'form' : form})


@login_required
def return_book(request, id):

    book = get_object_or_404(Book, pk=id)
    book.buyers.remove(request.user)

    book.quantity += 1
    book.save()
    
    user_account = get_object_or_404(UserAccount, user=request.user)
    
    user_account.balance += book.price
    user_account.save()
    
    return redirect("homepage")
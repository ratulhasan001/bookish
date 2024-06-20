from django.views.generic import CreateView
from .models import Transaction
from .forms import DepositForm
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib import messages

# Create your views here.
def send_transaction_email(user, amount, subject, template):
        message = render_to_string(template, {
            'user' : user,
            'amount' : amount,
        })
        send_email = EmailMultiAlternatives(subject, '', to=[user.email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()
        
class DepositView(CreateView, LoginRequiredMixin):
    template_name = 'deposit.html'
    model = Transaction
    form_class = DepositForm
    success_url = reverse_lazy('homepage')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs
    
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance += amount 
        account.save(
            update_fields=[
                'balance'
            ]
        )
        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully'
        )
        send_transaction_email(self.request.user, amount, "Deposite Message", "deposit_email.html")
        return super().form_valid(form)
    
    
    
class TransactionReportView(ListView, LoginRequiredMixin):
    model = Transaction
    template_name = 'transcation_report.html'
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(
            user=self.request.user.account
        )
        
        return queryset
    
    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(*args,**kwargs)
        context['transactions'] = self.get_queryset()
        
        return context
    
    
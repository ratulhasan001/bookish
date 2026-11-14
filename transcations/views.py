from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from accounts.models import UserAccount

from .forms import DepositForm
from .models import Transaction


def send_transaction_email(user, amount, subject, template):
    message = render_to_string(template, {
        'user': user,
        'amount': amount,
    })
    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()


class AccountMixin(LoginRequiredMixin):
    def get_account(self):
        # Users created outside the sign-up form (e.g. createsuperuser) get an
        # account on first use.
        if not hasattr(self, '_account'):
            self._account, _ = UserAccount.objects.get_or_create(user=self.request.user)
        return self._account


class DepositView(AccountMixin, CreateView):
    template_name = 'deposit.html'
    model = Transaction
    form_class = DepositForm
    success_url = reverse_lazy('transaction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.get_account()
        })
        return kwargs

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.get_account()
        with transaction.atomic():
            account.balance += amount
            account.save(update_fields=['balance'])
            response = super().form_valid(form)
        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully'
        )
        send_transaction_email(self.request.user, amount, "Deposit Message", "deposit_email.html")
        return response


class TransactionReportView(AccountMixin, ListView):
    model = Transaction
    template_name = 'transcation_report.html'

    def get_queryset(self):
        queryset = super().get_queryset().filter(account=self.get_account())
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(self.request, 'Please enter valid dates to filter the report.')
            else:
                queryset = queryset.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['account'] = self.get_account()
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        return context

from django import forms

from .constants import DEPOSIT
from .models import Transaction


class DepositForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount']

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
        return amount

    def save(self, commit=True):
        transaction = super().save(commit=False)
        transaction.user = self.account
        transaction.account = self.account
        transaction.transaction_type = DEPOSIT
        transaction.balance_after_transaction = self.account.balance

        transaction.save()

        return transaction

from decimal import Decimal

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserAccount

from .constants import DEPOSIT
from .models import Transaction


class DepositTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('sam', 'sam@example.com', 'pass-12345-word')
        UserAccount.objects.create(user=self.user, balance=10)

    def test_deposit_requires_login(self):
        response = self.client.post(reverse('deposit_money'), {'amount': 50})
        self.assertRedirects(response, f"{reverse('user_login')}?next={reverse('deposit_money')}")
        self.assertFalse(Transaction.objects.exists())

    def test_deposit(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('deposit_money'), {'amount': '90'})
        self.assertRedirects(response, reverse('transaction_report'))
        self.user.account.refresh_from_db()
        self.assertEqual(self.user.account.balance, Decimal('100'))
        transaction = Transaction.objects.get()
        self.assertEqual(transaction.transaction_type, DEPOSIT)
        self.assertEqual(transaction.balance_after_transaction, Decimal('100'))
        self.assertEqual(len(mail.outbox), 1)

    def test_non_positive_deposit_rejected(self):
        self.client.force_login(self.user)
        for amount in (0, -5):
            response = self.client.post(reverse('deposit_money'), {'amount': amount})
            self.assertContains(response, 'Amount must be greater than zero')
        self.user.account.refresh_from_db()
        self.assertEqual(self.user.account.balance, 10)

    def test_report_shows_only_own_transactions_and_filters(self):
        other = User.objects.create_user('other', 'o@example.com', 'pass-12345-word')
        other_account = UserAccount.objects.create(user=other)
        Transaction.objects.create(user=other_account, account=other_account, amount=1,
                                   balance_after_transaction=1, transaction_type=DEPOSIT)
        own = Transaction.objects.create(user=self.user.account, account=self.user.account, amount=2,
                                         balance_after_transaction=12, transaction_type=DEPOSIT)
        self.client.force_login(self.user)
        response = self.client.get(reverse('transaction_report'))
        self.assertEqual(list(response.context['object_list']), [own])

        day = own.timestamp.date().isoformat()
        response = self.client.get(reverse('transaction_report'), {'start_date': day, 'end_date': day})
        self.assertEqual(list(response.context['object_list']), [own])
        response = self.client.get(reverse('transaction_report'), {'start_date': '2000-01-01', 'end_date': '2000-01-02'})
        self.assertEqual(list(response.context['object_list']), [])
        response = self.client.get(reverse('transaction_report'), {'start_date': 'x', 'end_date': 'y'})
        self.assertEqual(response.status_code, 200)

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from book.tests import make_book

from .models import UserAccount


class AccountTests(TestCase):
    def test_register_creates_account_with_zero_balance(self):
        response = self.client.post(reverse('register'), {
            'username': 'newbie', 'first_name': 'New', 'last_name': 'Bie', 'email': 'n@example.com',
            'password1': 'pass-12345-word', 'password2': 'pass-12345-word',
        })
        self.assertRedirects(response, reverse('user_login'))
        self.assertEqual(User.objects.get(username='newbie').account.balance, 0)

    def test_login_and_post_only_logout(self):
        User.objects.create_user('sam', 'sam@example.com', 'pass-12345-word')
        response = self.client.post(reverse('user_login'), {'username': 'sam', 'password': 'pass-12345-word'})
        self.assertRedirects(response, reverse('homepage'))
        self.assertEqual(self.client.get(reverse('user_logout')).status_code, 405)
        response = self.client.post(reverse('user_logout'))
        self.assertRedirects(response, reverse('user_login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_pages_require_login(self):
        for name in ('profile', 'edit_profile', 'pass_change', 'deposit_money', 'transaction_report'):
            response = self.client.get(reverse(name))
            self.assertRedirects(response, f"{reverse('user_login')}?next={reverse(name)}", msg_prefix=name)


class PageSmokeTests(TestCase):
    def setUp(self):
        self.book = make_book()

    def test_public_pages(self):
        urls = [reverse('homepage'), reverse('genre_wise_post', args=['sci-fi']),
                reverse('book_details', args=[self.book.id]), reverse('user_login'), reverse('register')]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        self.assertEqual(self.client.get(reverse('genre_wise_post', args=['missing'])).status_code, 404)

    def test_logged_in_pages(self):
        user = User.objects.create_user('sam', 'sam@example.com', 'pass-12345-word')
        UserAccount.objects.create(user=user, balance=500)
        self.book.buyers.add(user)
        self.client.force_login(user)
        for name in ('homepage', 'profile', 'edit_profile', 'pass_change', 'deposit_money', 'transaction_report'):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)
        response = self.client.get(reverse('book_details', args=[self.book.id]))
        self.assertContains(response, 'Add Review')

    def test_superuser_without_account(self):
        admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin-pass-123')
        self.client.force_login(admin)
        for name in ('homepage', 'profile', 'deposit_money', 'transaction_report'):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

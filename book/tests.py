from decimal import Decimal

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserAccount
from genres.models import Genres
from transcations.constants import BORROW, RETURN
from transcations.models import Transaction

from .models import Book, Review


def make_user(username='reader', balance=0):
    user = User.objects.create_user(username, f'{username}@example.com', 'pass-12345-word')
    UserAccount.objects.create(user=user, balance=balance)
    return user


def make_book(**kwargs):
    defaults = dict(title='Dune', price=Decimal('120'), author='Frank Herbert',
                    description='Sand.', quantity=2, image='book/media/images/dune.jpg')
    defaults.update(kwargs)
    book = Book.objects.create(**defaults)
    genre, _ = Genres.objects.get_or_create(name='Sci-Fi', slug='sci-fi')
    book.genres.add(genre)
    return book


class BorrowReturnTests(TestCase):
    def setUp(self):
        self.user = make_user(balance=200)
        self.book = make_book()
        self.borrow_url = reverse('borrow_book', args=[self.book.id])
        self.return_url = reverse('return_book', args=[self.book.id])
        self.client.force_login(self.user)

    def refresh(self):
        self.book.refresh_from_db()
        self.user.account.refresh_from_db()

    def test_borrow_deducts_price_and_stock(self):
        response = self.client.post(self.borrow_url)
        self.assertRedirects(response, reverse('book_details', args=[self.book.id]))
        self.refresh()
        self.assertEqual(self.book.quantity, 1)
        self.assertEqual(self.user.account.balance, Decimal('80'))
        self.assertIn(self.user, self.book.buyers.all())
        self.assertEqual(Transaction.objects.get().transaction_type, BORROW)
        self.assertEqual(len(mail.outbox), 1)

    def test_borrow_requires_login_and_post(self):
        self.assertEqual(self.client.get(self.borrow_url).status_code, 405)
        self.client.logout()
        response = self.client.post(self.borrow_url)
        self.assertRedirects(response, f"{reverse('user_login')}?next={self.borrow_url}")
        self.refresh()
        self.assertEqual(self.book.quantity, 2)
        self.assertEqual(self.user.account.balance, 200)

    def test_borrow_with_insufficient_balance(self):
        poor = make_user('poor', balance=50)
        self.client.force_login(poor)
        self.client.post(self.borrow_url)
        self.refresh()
        poor.account.refresh_from_db()
        self.assertEqual(self.book.quantity, 2)
        self.assertEqual(poor.account.balance, 50)
        self.assertFalse(Transaction.objects.exists())

    def test_cannot_borrow_twice(self):
        self.client.post(self.borrow_url)
        self.client.post(self.borrow_url)
        self.refresh()
        self.assertEqual(self.book.quantity, 1)
        self.assertEqual(self.user.account.balance, Decimal('80'))

    def test_cannot_borrow_out_of_stock(self):
        self.book.quantity = 0
        self.book.save()
        self.client.post(self.borrow_url)
        self.refresh()
        self.assertEqual(self.book.quantity, 0)
        self.assertEqual(self.user.account.balance, 200)

    def test_return_refunds(self):
        self.client.post(self.borrow_url)
        response = self.client.post(self.return_url)
        self.assertRedirects(response, reverse('profile'))
        self.refresh()
        self.assertEqual(self.book.quantity, 2)
        self.assertEqual(self.user.account.balance, Decimal('200'))
        self.assertNotIn(self.user, self.book.buyers.all())
        self.assertEqual(Transaction.objects.last().transaction_type, RETURN)

    def test_cannot_return_unborrowed_book(self):
        response = self.client.post(self.return_url)
        self.assertRedirects(response, reverse('profile'))
        self.refresh()
        self.assertEqual(self.book.quantity, 2)
        self.assertEqual(self.user.account.balance, 200)

    def test_return_rejects_get(self):
        self.client.post(self.borrow_url)
        self.assertEqual(self.client.get(self.return_url).status_code, 405)


class ReviewTests(TestCase):
    def setUp(self):
        self.user = make_user(balance=500)
        self.book = make_book()
        self.url = reverse('book_details', args=[self.book.id])

    def test_borrower_can_review(self):
        self.book.buyers.add(self.user)
        self.client.force_login(self.user)
        response = self.client.post(self.url, {'body': 'Great read'})
        self.assertRedirects(response, self.url)
        review = Review.objects.get()
        self.assertEqual(review.name, 'reader')
        self.assertEqual(review.email, 'reader@example.com')

    def test_non_borrower_cannot_review(self):
        self.client.force_login(self.user)
        self.client.post(self.url, {'body': 'Spam'})
        self.assertFalse(Review.objects.exists())

    def test_anonymous_cannot_review(self):
        response = self.client.post(self.url, {'body': 'Spam'})
        self.assertRedirects(response, reverse('user_login'))
        self.assertFalse(Review.objects.exists())

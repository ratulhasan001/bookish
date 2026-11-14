# Bookish

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white)

One of my early Django projects, built in 2024 while I was learning the framework.

Bookish is a small web application for borrowing books with a simple account balance. Registered users deposit money into their account, browse books by genre, borrow a book (its price is deducted from their balance), return it for a refund, and review books they have borrowed.

## What I practised

- User authentication (registration, login, profile editing, password change)
- Relational models across several apps, including many-to-many relations
- Class-based and function-based views
- Image uploads and serving static files
- Keeping balances and stock consistent with database transactions
- HTML email notifications and environment-based configuration

## Features

- **Accounts**: registration, login, logout, profile editing and password change. Each new user gets an account with a starting balance of 0.
- **Catalogue**: the home page lists all books with cover image, author, price and stock, plus genre buttons that filter the list (`/genre/<slug>/`).
- **Book details**: a detail page shows the book, its remaining stock and all reviews.
- **Borrowing**: a logged-in user can borrow a book that is in stock, if they have not already borrowed it and their balance covers the price. This lowers the stock by one, records the user as a borrower, deducts the price, records a transaction and sends a confirmation email.
- **Returning**: borrowed books appear on the user's profile page with a "Return Book" button, which restores the stock, refunds the price and records a transaction.
- **Reviews**: only users who have borrowed a book can review it. The review uses the reader's username and email.
- **Deposits**: users deposit money into their balance. Each deposit is stored as a transaction and confirmed by email.
- **Transaction report**: deposits, borrows and returns with a date-range filter and the current balance.
- **Admin**: books, reviews, genres (slug auto-filled from the name), user accounts and transactions are managed in the Django admin.

## Tech stack

| | |
| --- | --- |
| Language | Python 3 |
| Framework | Django 4.2 |
| Database | Any database supported by `dj-database-url` (SQLite by default, PostgreSQL in deployment) |
| Configuration | django-environ |
| Forms | django-crispy-forms with crispy-bootstrap5 |
| Images | Pillow (`ImageField` for book covers) |
| Email | Console output locally, SMTP (Gmail) when configured |
| Front end | Django templates, Bootstrap 5.3 and Tailwind CSS 1.x (CDN) |

## Project structure

```
bookish/
├── manage.py
├── requirements.txt
├── .env.example
├── bookish/        # settings and root URLconf
├── accounts/       # registration, login, profile, returning books, UserAccount (balance)
├── book/           # Book and Review models, detail view, borrowing
├── genres/         # Genre model used for filtering
├── transcations/   # deposits and transaction report
├── core/           # home page and base template
└── static/         # site images
```

## Getting started

```bash
git clone https://github.com/ratulhasan001/bookish.git
cd bookish

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/. No configuration file is needed: without one the app uses a local SQLite database (`db.sqlite3`) and prints emails to the terminal. Add genres and books (with cover images) in the admin at `/admin/`, then register a normal user through the site to deposit, borrow and review. Uploaded covers are stored in `media/`.

### Configuration (optional)

Settings are read from environment variables or from `bookish/.env` (next to `settings.py`). Copy `.env.example` as a starting point.

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Django secret key. A development key is used when unset. |
| `DEBUG` | `True` by default. Set to `False` in production. |
| `DATABASE_URL` | Database connection string. Defaults to `sqlite:///db.sqlite3`. |
| `EMAIL`, `EMAIL_PASSWORD` | Gmail address and app password for SMTP. Without `EMAIL`, emails are printed to the console. |

## Running the tests

```bash
python manage.py test
```

The tests cover registration, login and logout, borrowing (success, insufficient balance, out of stock, borrowing twice, login and POST requirements), returning and refunds, reviews, deposits, the transaction report filter and a smoke test of the main pages.

## Later improvements

After the original coursework I went back and fixed the following:

- Borrowing and returning are POST-only and require login. The server now checks stock, balance and whether the book is already borrowed, and a book can only be returned (and refunded) by someone who borrowed it.
- Borrows and returns are recorded as transactions and appear in the report, and the report's date filter now works.
- Only borrowers can post reviews, and the review form markup was fixed.
- Deposits must be positive, and the deposit and report pages require login (`LoginRequiredMixin` now comes first in the class bases).
- An unknown genre in the URL returns a 404 instead of an error page.
- Logout is a POST form, which keeps it working on Django 5.
- The app runs locally with no `.env` (SQLite, console email), and the hardcoded secret key was removed.
- Small UI fixes: active navigation links, a footer, coloured messages, empty states, page titles and the "Author" label on book cards.
- Added an automated test suite.

## Author

Ratul Hasan · [ratulhasan.dev](https://ratulhasan.dev)

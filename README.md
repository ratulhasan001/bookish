# Bookish

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white)

Bookish is a Django web application for borrowing books with a simple account balance system. Registered users deposit money into their account, browse books by genre, borrow a book (its price is deducted from their balance), return it for a refund, and review books they have borrowed. The project demonstrates user authentication, relational models across several apps, class-based and function-based views, image uploads, environment-based configuration and HTML email notifications.

## Features

- **Accounts**: registration, login, logout, profile editing and password change. Each new user gets an account with a starting balance of 0.
- **Catalogue**: the home page lists all books with cover image, price and stock, plus genre buttons that filter the list (`/genre/<slug>/`).
- **Book details**: a detail page shows the book, its remaining stock and all reviews.
- **Borrowing**: a logged-in user can borrow a book. This lowers the stock by one, records the user as a borrower, deducts the price from their balance and sends a confirmation email.
- **Returning**: borrowed books appear on the user's profile page with a "Return Book" button, which restores the stock and refunds the price.
- **Reviews**: the review form appears only to users who have borrowed that book.
- **Deposits**: users deposit money into their balance. Each deposit is stored as a transaction and confirmed by email.
- **Transaction report**: a page listing the user's transactions and current balance.
- **Admin**: books, reviews, genres (slug auto-filled from the name), user accounts and transactions are managed in the Django admin.

## Tech stack

| | |
| --- | --- |
| Language | Python 3 |
| Framework | Django 4.2 |
| Database | Any database supported by `dj-database-url` (PostgreSQL in deployment, SQLite works locally) |
| Configuration | django-environ |
| Forms | django-crispy-forms with crispy-bootstrap5 |
| Images | Pillow (`ImageField` for book covers) |
| Email | SMTP (Gmail) |
| Front end | Django templates, Bootstrap 5.3 and Tailwind CSS 1.x (CDN) |

## Project structure

```
bookish/
├── manage.py
├── requirements.txt
├── bookish/        # settings and root URLconf
├── accounts/       # registration, login, profile, UserAccount (balance)
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
```

Create a file `bookish/.env` (in the same folder as `settings.py`) with these variables. You can also export them in your shell.

```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
EMAIL=your-address@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
```

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Django secret key |
| `DATABASE_URL` | Database connection string. Use `sqlite:///db.sqlite3` for local development. |
| `EMAIL` | SMTP username (Gmail address) used to send notifications |
| `EMAIL_PASSWORD` | SMTP password (a Gmail app password) |

Then set up the database and start the server:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/. Add genres and books (with cover images) in the admin at `/admin/`, then register a normal user through the site to deposit, borrow and review. Deposits and borrowing send email, so they need valid SMTP credentials.

## Author

Ratul Hasan · [ratulhasan.dev](https://ratulhasan.dev)

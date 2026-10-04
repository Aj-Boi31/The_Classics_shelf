# The Classics Shelf

The Classics Shelf is a personal book catalogue for classic literature, built with Django for CSC1025 Project 02 (2026). Visitors can browse the full collection that they have added complete with cover art, author, publication year, genre, and synopsis with the order shuffled on every visit so something new always catches the eye. A genre list narrows the shelf to a specific flavour of reading, while individual detail pages let users step through the catalogue one book at a time. Registered users get more: they can toggle a heart to save favourites to their own private reading list, submit entirely new titles complete with an uploaded cover image, and remove entries they no longer want on the shelf. The whole site is backed by Django's authentication system and an admin panel wired up for fast search and filtering across all three models.

---

## Screenshots

![Browse the shelf, filter by genre](docs/home.png)

![Book detail page with previous / next navigation](docs/book-detail.png)

---

## Features

- **Browse & discover** — book catalogue displayed in randomised order on every load, with cover images, author, year, genre, and description
- **Filter by genre** — dropdown filter applied via `get_queryset()` override on the list view
- **Book detail pages** — with prev/next navigation across the full catalogue
- **User auth** — register, login, and logout using Django's built-in auth system
- **Favourites** — logged-in users can toggle any book as a favourite; a dedicated page lists their saved books
- **Add & delete books** — authenticated users can submit new books with cover image uploads; delete is also protected
- **Contact form** — validated Django form with success flash message
- **Admin panel** — fully configured with search, filtering, and ordering on all three models

---

## Tech Stack

| Layer       | Technology          |
|-------------|---------------------|
| Framework   | Django 6.0          |
| Language    | Python 3.14         |
| Frontend    | Bootstrap 5 (CDN)   |
| Database    | SQLite              |
| Images      | Pillow (ImageField) |

---

## Running It Locally

This project isn't hosted online — clone the repo and run it locally to try it out.

```bash
# 1. Clone the repo
git clone https://github.com/Aj-Boi31/The_Classics_shelf.git
cd The_Classics_shelf

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. (Optional) create an admin account
python manage.py createsuperuser

# 6. Run the dev server
python manage.py runserver
```

Then visit `http://127.0.0.1:8000/` in your browser. Register an account to add books, mark favourites, and try the full authenticated flow.

---

## Project Structure

```
book_project/          # Project config (settings, urls, wsgi)
books/                 # Core app — models, views, urls, admin, forms, templates
accounts/              # Auth app — register, login, logout views and templates
media/                 # Uploaded cover images (covers/)
static/                # Static assets
templates/             # Base templates
```

---

## Models

- **Genre** — `name` (CharField); linked to Book via ForeignKey
- **Book** — `title`, `author`, `year_published`, `genre` (FK), `description`, `cover_image` (ImageField)
- **Favourite** — `user` (FK), `book` (FK), `added_on` (auto); enforces `unique_together` to prevent duplicate saves

---

## Key Django Patterns Used

- Class-based views (`ListView`, `DetailView`, `CreateView`, `DeleteView`) with `LoginRequiredMixin`
- `get_queryset()` override for randomised display and genre filtering
- `get_context_data()` override to pass favourites status and prev/next book navigation
- Function-based view with `@login_required` for the favourite toggle
- Django's built-in `UserCreationForm` and `AuthenticationForm` for auth
- `ImageField` with Pillow for book cover uploads
- Custom `ModelAdmin` classes with `list_display`, `search_fields`, `list_filter`, and `ordering`

---

## Testing

```bash
python manage.py test
```

Nine tests cover genre filtering on the shelf, login protection on the add / delete / favourites views, the favourite toggle (add then remove), favourites staying private to each user, and the detail page's previous / next navigation and 404 handling.

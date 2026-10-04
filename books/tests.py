from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Book, Favourite, Genre


class BookTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.gothic = Genre.objects.create(name="Gothic")
        cls.romance = Genre.objects.create(name="Romance")
        cls.frankenstein = Book.objects.create(
            title="Frankenstein", author="Mary Shelley", year_published=1818,
            genre=cls.gothic, description="A scientist creates life.",
        )
        cls.pride = Book.objects.create(
            title="Pride and Prejudice", author="Jane Austen", year_published=1813,
            genre=cls.romance, description="Manners and marriage.",
        )
        cls.user = User.objects.create_user("reader", password="pass12345")


class BookListTests(BookTestCase):
    def test_lists_every_book_without_a_filter(self):
        response = self.client.get(reverse("book_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["books"]), 2)

    def test_genre_filter_narrows_the_shelf(self):
        response = self.client.get(reverse("book_list"), {"genre": self.gothic.id})
        titles = [b.title for b in response.context["books"]]
        self.assertEqual(titles, ["Frankenstein"])


class LoginProtectionTests(BookTestCase):
    def test_add_book_requires_login(self):
        response = self.client.get(reverse("book_add"))
        self.assertRedirects(response, f"/accounts/login/?next={reverse('book_add')}")

    def test_delete_requires_login(self):
        url = reverse("book_delete", args=[self.frankenstein.pk])
        self.assertEqual(self.client.post(url).status_code, 302)
        self.assertTrue(Book.objects.filter(pk=self.frankenstein.pk).exists())

    def test_favourites_page_requires_login(self):
        response = self.client.get(reverse("favourites"))
        self.assertEqual(response.status_code, 302)


class FavouriteTests(BookTestCase):
    def test_toggle_adds_then_removes_a_favourite(self):
        self.client.login(username="reader", password="pass12345")
        url = reverse("favourite_toggle", args=[self.pride.pk])
        self.client.get(url)
        self.assertTrue(Favourite.objects.filter(user=self.user, book=self.pride).exists())
        self.client.get(url)
        self.assertFalse(Favourite.objects.filter(user=self.user, book=self.pride).exists())

    def test_favourites_are_private_to_each_user(self):
        other = User.objects.create_user("other", password="pass12345")
        Favourite.objects.create(user=other, book=self.pride)
        self.client.login(username="reader", password="pass12345")
        response = self.client.get(reverse("favourites"))
        self.assertEqual(len(response.context["favourites"]), 0)


class DetailPageTests(BookTestCase):
    def test_detail_page_loads_with_prev_and_next(self):
        response = self.client.get(reverse("book_detail", args=[self.frankenstein.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["next_book"], self.pride)

    def test_missing_book_returns_404(self):
        self.assertEqual(self.client.get(reverse("book_detail", args=[9999])).status_code, 404)

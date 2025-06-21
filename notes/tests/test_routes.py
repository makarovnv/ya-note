from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note


User = get_user_model()


class NotesRoutesAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(
            username='author',
            password='pass'
        )
        self.other_user = User.objects.create_user(
            username='other',
            password='pass'
        )
        self.note = Note.objects.create(
            title='Test Note',
            text='Some text',
            slug='test-note',
            author=self.author,
        )
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.other_client = Client()
        self.other_client.force_login(self.other_user)

    def test_anonymous_accessible_pages(self):
        pages = [
            ('notes:home', None, HTTPStatus.OK),
            ('users:login', None, HTTPStatus.OK),
            ('users:signup', None, HTTPStatus.OK),
        ]
        for name, args, expected_status in pages:
            with self.subTest(page=name):
                url = reverse(name) if args is None else reverse(
                    name,
                    args=args
                )
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_users_logout_only_post(self):
        url = reverse('users:logout')
        with self.subTest('GET logout should be 405'):
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                HTTPStatus.METHOD_NOT_ALLOWED
            )
        with self.subTest('POST logout should redirect'):
            response = self.client.post(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_accessible_pages(self):
        pages = [
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        ]
        for name, args in pages:
            with self.subTest(user='author', page=name):
                url = reverse(name) if args is None else reverse(
                    name,
                    args=args
                )
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
            with self.subTest(user='other', page=name):
                url = reverse(name) if args is None else reverse(
                    name,
                    args=args
                )
                response = self.other_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_only_pages(self):
        pages = [
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        ]
        for name, args in pages:
            url = reverse(name, args=args)
            with self.subTest(user='author', page=name):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
            with self.subTest(user='other', page=name):
                response = self.other_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonymous_redirects_to_login(self):
        pages = [
            'notes:list',
            'notes:add',
            'notes:success',
            'notes:detail',
            'notes:edit',
            'notes:delete',
        ]
        for name in pages:
            if any(action in name for action in ('detail', 'edit', 'delete')):
                args = (self.note.slug,)
            else:
                args = None
            with self.subTest(page=name):
                url = reverse(name, args=args) if args else reverse(name)
                response = self.client.get(url)
                login_url = reverse('users:login')
                expected_redirect = f'{login_url}?next={url}'
                self.assertRedirects(response, expected_redirect)

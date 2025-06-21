from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='user')
        cls.reader = User.objects.create(username='user1')
        cls.note = Note.objects.create(
            title='test',
            author=cls.author,
            text='Текст комментария',
            slug='test'
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', None, None, HTTPStatus.OK),
            ('notes:detail', (self.note.slug,), self.author, HTTPStatus.OK),
            (
                'notes:detail',
                (self.note.slug,),
                self.reader,
                HTTPStatus.NOT_FOUND
            ),
            ('notes:list', None, self.author, HTTPStatus.OK),
            ('notes:list', None, None, HTTPStatus.FOUND),
            ('users:login', None, None, HTTPStatus.OK),
            ('users:logout', None, self.author, HTTPStatus.OK),
            ('users:signup', None, None, HTTPStatus.OK),
            ('notes:add', None, self.author, HTTPStatus.OK),
            ('notes:add', None, None, HTTPStatus.FOUND),
        )

        for name, args, user, expected_status in urls:
            with self.subTest(name=name, user=user):
                if user:
                    self.client.force_login(user)
                else:
                    self.client.logout()
                url = reverse(name, args=args)
                if name == 'users:logout':
                    method = self.client.post
                else:
                    method = self.client.get
                response = method(url)

                if expected_status == HTTPStatus.FOUND:
                    login_url = reverse('users:login')
                    expected_redirect = f'{login_url}?next={url}'
                    self.assertRedirects(response, expected_redirect)
                else:
                    self.assertEqual(response.status_code, expected_status)

    def test_edit_and_delete_pages_access(self):
        slug = self.note.slug

        urls = (
            ('notes:detail', (slug,), self.author, HTTPStatus.OK),
            ('notes:detail', (slug,), self.reader, HTTPStatus.NOT_FOUND),
            ('notes:edit', (slug,), self.author, HTTPStatus.OK),
            ('notes:edit', (slug,), self.reader, HTTPStatus.NOT_FOUND),
            ('notes:delete', (slug,), self.author, HTTPStatus.OK),
            ('notes:delete', (slug,), self.reader, HTTPStatus.NOT_FOUND),
        )

        for name, args, user, expected_status in urls:
            with self.subTest(name=name, user=user):
                self.client.force_login(user)
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status)

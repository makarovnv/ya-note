from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class NotesContentTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            password='pass'
        )
        self.other_user = User.objects.create_user(
            username='other',
            password='pass'
        )
        self.note_author = Note.objects.create(
            title='Author Note',
            text='Text',
            slug='author-note',
            author=self.author
        )
        self.note_other = Note.objects.create(
            title='Other Note',
            text='Other text',
            slug='other-note',
            author=self.other_user
        )
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_note_in_object_list_for_author(self):
        url = reverse('notes:list')
        response = self.author_client.get(url)
        self.assertIn('object_list', response.context)
        notes = response.context['object_list']
        self.assertIn(self.note_author, notes)
        self.assertNotIn(self.note_other, notes)

    def test_forms_in_create_and_edit_pages(self):
        pages = [
            ('notes:add', None),
            ('notes:edit', (self.note_author.slug,)),
        ]
        for name, args in pages:
            with self.subTest(page=name):
                url = reverse(name) if args is None else reverse(
                    name,
                    args=args
                )
                response = self.author_client.get(url)
                self.assertIn('form', response.context)

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm, WARNING
from notes.models import Note


User = get_user_model()


class NoteFormTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')

    def test_slug_autogeneration(self):
        data = {
            'title': 'Тестовая заметка',
            'text': 'Текст',
            'slug': '',
        }
        form = NoteForm(data=data)
        self.assertTrue(form.is_valid())
        note = form.save(commit=False)
        note.author = self.author
        note.save()
        self.assertEqual(note.slug, 'testovaya-zametka')

    def test_slug_uniqueness_validation(self):
        Note.objects.create(
            title='Тестовая заметка',
            text='Текст',
            slug='testovaya-zametka',
            author=self.author
        )

        data = {
            'title': 'Другая заметка',
            'text': 'Другой текст',
            'slug': 'testovaya-zametka',
        }
        form = NoteForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('slug', form.errors)
        error_text = form.errors['slug'][0]
        self.assertIn(WARNING.strip(), error_text)

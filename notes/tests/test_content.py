from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class NoteCreateViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='author',
            password='pass123'
        )

    def setUp(self):
        self.client.login(username='author', password='pass123')
        self.url = reverse('notes:add')

    def test_post_create_note(self):
        data = {
            'title': 'Новая заметка',
            'text': 'Текст заметки',
            'slug': 'new_note',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        from notes.models import Note
        note = Note.objects.get(title='Новая заметка')
        self.assertEqual(note.author, self.user)

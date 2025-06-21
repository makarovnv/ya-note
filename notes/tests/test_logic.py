
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from pytils.translit import slugify

from notes.models import Note


User = get_user_model()


class NotesLogicTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            password='pass'
        )
        self.other_user = User.objects.create_user(
            username='other',
            password='pass'
        )
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.other_client = Client()
        self.other_client.force_login(self.other_user)
        self.anon_client = Client()

    def test_logged_in_user_can_create_note(self):
        url = reverse('notes:add')
        data = {'title': 'New Note', 'text': 'Some text', 'slug': 'new-note'}
        response = self.author_client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Note.objects.filter(
            slug='new-note',
            author=self.author
        ).exists())

    def test_anonymous_cannot_create_note(self):
        url = reverse('notes:add')
        data = {'title': 'New Note', 'text': 'Some text', 'slug': 'new-note'}
        response = self.anon_client.post(url, data)
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(Note.objects.filter(slug='new-note').exists())

    def test_cannot_create_two_notes_with_same_slug(self):
        Note.objects.create(
            title='Note1',
            text='text',
            slug='same-slug',
            author=self.author
        )
        url = reverse('notes:add')
        data = {'title': 'Note2', 'text': 'other text', 'slug': 'same-slug'}
        response = self.author_client.post(url, data)
        form = response.context.get('form')
        self.assertIsNotNone(form)
        self.assertIn('slug', form.errors)

    def test_slug_is_auto_generated_if_blank(self):
        url = reverse('notes:add')
        data = {'title': 'Auto Slug Title', 'text': 'Text', 'slug': ''}
        response = self.author_client.post(url, data)
        note = Note.objects.filter(title='Auto Slug Title', author=self.author).first()
        self.assertIsNotNone(note)
        self.assertEqual(
            note.slug,
            slugify(note.title)[:note._meta.get_field('slug').max_length]
        )

    def test_user_can_edit_and_delete_own_note(self):
        note = Note.objects.create(
            title='EditMe',
            text='text',
            slug='editme',
            author=self.author
        )
        edit_url = reverse('notes:edit', args=(note.slug,))
        delete_url = reverse('notes:delete', args=(note.slug,))
        response_edit = self.author_client.get(edit_url)
        response_delete = self.author_client.get(delete_url)
        self.assertEqual(response_edit.status_code, 200)
        self.assertEqual(response_delete.status_code, 200)

    def test_user_cannot_edit_or_delete_others_note(self):
        note = Note.objects.create(
            title='OtherNote',
            text='text',
            slug='othernote',
            author=self.other_user
        )
        edit_url = reverse('notes:edit', args=(note.slug,))
        delete_url = reverse('notes:delete', args=(note.slug,))
        response_edit = self.author_client.get(edit_url)
        response_delete = self.author_client.get(delete_url)
        self.assertEqual(response_edit.status_code, 404)
        self.assertEqual(response_delete.status_code, 404)

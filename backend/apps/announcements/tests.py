from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.announcements.models import Announcement

User = get_user_model()


def make_user(phone, role='member', password='123456'):
    u = User(phone=phone, username=phone, role=role)
    u.set_password(password)
    u.save()
    return u


class AnnouncementTests(APITestCase):
    def setUp(self):
        self.published = Announcement.objects.create(title='已发布', content='内容', is_published=True)
        self.draft = Announcement.objects.create(title='草稿', content='内容', is_published=False)

    def test_guest_sees_only_published(self):
        r = self.client.get('/api/announcements/')
        self.assertEqual(r.status_code, 200)
        titles = [a['title'] for a in r.data['results']]
        self.assertIn('已发布', titles)
        self.assertNotIn('草稿', titles)

    def test_guest_cannot_create(self):
        r = self.client.post('/api/announcements/', {'title': 'x', 'content': 'y'})
        self.assertEqual(r.status_code, 401)

    def test_staff_toggle_publish(self):
        admin = make_user('13800000000', role='admin')
        self.client.force_authenticate(user=admin)
        r = self.client.post(f'/api/announcements/{self.draft.id}/toggle_publish/')
        self.assertEqual(r.status_code, 200)
        self.draft.refresh_from_db()
        self.assertTrue(self.draft.is_published)

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.activities.models import Activity, Registration
from apps.venues.models import Venue

User = get_user_model()


def make_user(phone, role='member', password='123456'):
    u = User(phone=phone, username=phone, role=role)
    u.set_password(password)
    u.save()
    return u


def make_activity(capacity=10, days=3, is_active=True):
    venue = Venue.objects.create(name='测试场馆')
    now = timezone.now()
    return Activity.objects.create(
        venue=venue, title='周末比赛', type='match', capacity=capacity,
        start_at=now + timedelta(days=days, hours=1),
        end_at=now + timedelta(days=days, hours=3),
        price='0.00', deadline=now + timedelta(days=days),
        is_active=is_active,
    )


class ActivityTests(APITestCase):
    def setUp(self):
        self.member = make_user('13800000001')
        self.client.force_authenticate(user=self.member)

    def test_member_cannot_create(self):
        r = self.client.post('/api/activities/', {
            'venue': Venue.objects.create(name='x').id, 'title': 'x', 'type': 'match',
            'start_at': timezone.now(), 'end_at': timezone.now(), 'capacity': 1,
            'deadline': timezone.now(),
        })
        self.assertEqual(r.status_code, 403)

    def test_register_success(self):
        a = make_activity()
        r = self.client.post(f'/api/activities/{a.id}/register/')
        self.assertEqual(r.status_code, 200)
        a.refresh_from_db()
        self.assertEqual(a.registered, 1)

    def test_register_duplicate_rejected(self):
        a = make_activity()
        self.client.post(f'/api/activities/{a.id}/register/')
        r = self.client.post(f'/api/activities/{a.id}/register/')
        self.assertEqual(r.status_code, 400)
        a.refresh_from_db()
        self.assertEqual(a.registered, 1)

    def test_register_full_rejected(self):
        a = make_activity(capacity=1)
        other = make_user('13800000002')
        self.client.post(f'/api/activities/{a.id}/register/')
        self.client.force_authenticate(user=other)
        r = self.client.post(f'/api/activities/{a.id}/register/')
        self.assertEqual(r.status_code, 400)

    def test_register_after_deadline_rejected(self):
        a = make_activity()
        Activity.objects.filter(pk=a.pk).update(deadline=timezone.now() - timedelta(hours=1))
        r = self.client.post(f'/api/activities/{a.id}/register/')
        self.assertEqual(r.status_code, 400)

    def test_cancel_releases_and_reregister(self):
        a = make_activity()
        self.client.post(f'/api/activities/{a.id}/register/')
        r = self.client.post(f'/api/activities/{a.id}/cancel/')
        self.assertEqual(r.status_code, 200)
        a.refresh_from_db()
        self.assertEqual(a.registered, 0)
        r = self.client.post(f'/api/activities/{a.id}/register/')
        self.assertEqual(r.status_code, 200)
        a.refresh_from_db()
        self.assertEqual(a.registered, 1)

    def test_registrations_list_staff_only(self):
        a = make_activity()
        self.client.post(f'/api/activities/{a.id}/register/')
        r = self.client.get(f'/api/activities/{a.id}/registrations/')
        self.assertEqual(r.status_code, 403)
        admin = make_user('13800000000', role='admin')
        self.client.force_authenticate(user=admin)
        r = self.client.get(f'/api/activities/{a.id}/registrations/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['data']), 1)

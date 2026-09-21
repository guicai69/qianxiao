from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.bookings.models import Booking
from apps.venues.models import Venue, Court, TimeSlot

User = get_user_model()


def make_user(phone, role='member', password='123456'):
    u = User(phone=phone, username=phone, role=role)
    u.set_password(password)
    u.save()
    return u


class AvailabilityTests(APITestCase):
    def test_availability_returns_occupied_only(self):
        member = make_user('13800000001')
        other = make_user('13800000002')
        venue = Venue.objects.create(name='测试场馆')
        court = Court.objects.create(venue=venue, name='1号场')
        slot = TimeSlot.objects.create(venue=venue, start_time='10:00', end_time='11:00', price='100.00')
        tomorrow = timezone.localdate() + timedelta(days=1)
        Booking.objects.create(user=other, court=court, date=tomorrow, time_slot=slot, status='paid', amount='100.00')
        self.client.force_authenticate(user=member)
        r = self.client.get(f'/api/venues/{venue.id}/availability/', {'date': tomorrow.isoformat()})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['occupied'], [{'court_id': court.id, 'time_slot_id': slot.id}])

    def test_partial_update_cannot_break_time_order(self):
        admin = make_user('13800000000', role='admin')
        venue = Venue.objects.create(name='测试场馆')
        slot = TimeSlot.objects.create(venue=venue, start_time='10:00', end_time='11:00', price='100.00')
        self.client.force_authenticate(user=admin)
        r = self.client.patch(f'/api/time-slots/{slot.id}/', {'start_time': '11:30'})
        self.assertEqual(r.status_code, 400)
        slot.refresh_from_db()
        self.assertEqual(slot.start_time.strftime('%H:%M'), '10:00')


class SlotIntegrityTests(APITestCase):
    """t6 审查发现的正确性漏洞回归测试"""

    def setUp(self):
        self.admin = make_user('13800000000', role='admin')
        self.venue = Venue.objects.create(name='测试场馆')
        self.client.force_authenticate(user=self.admin)

    def test_negative_price_rejected(self):
        r = self.client.post('/api/time-slots/', {
            'venue': self.venue.id, 'start_time': '08:00', 'end_time': '09:00', 'price': '-50.00',
        })
        self.assertEqual(r.status_code, 400)

    def test_overlap_slot_rejected(self):
        TimeSlot.objects.create(venue=self.venue, start_time='10:00', end_time='11:00', price='100.00')
        r = self.client.post('/api/time-slots/', {
            'venue': self.venue.id, 'start_time': '10:30', 'end_time': '11:30', 'price': '100.00',
        })
        self.assertEqual(r.status_code, 400)

    def test_duplicate_court_name_rejected(self):
        Court.objects.create(venue=self.venue, name='1号场')
        r = self.client.post('/api/courts/', {'venue': self.venue.id, 'name': '1号场'})
        self.assertEqual(r.status_code, 400)

    def test_delete_venue_with_booking_returns_400(self):
        member = make_user('13800000001')
        court = Court.objects.create(venue=self.venue, name='1号场')
        slot = TimeSlot.objects.create(venue=self.venue, start_time='10:00', end_time='11:00', price='100.00')
        Booking.objects.create(
            user=member, court=court, date=timezone.localdate(), time_slot=slot,
            status='paid', amount='100.00',
        )
        r = self.client.delete(f'/api/venues/{self.venue.id}/')
        self.assertEqual(r.status_code, 400)

    def test_non_numeric_venue_filter_returns_400(self):
        r = self.client.get('/api/courts/', {'venue': 'abc'})
        self.assertEqual(r.status_code, 400)

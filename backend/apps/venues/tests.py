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

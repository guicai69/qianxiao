from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.bookings.models import Booking
from apps.venues.models import Venue, Court, TimeSlot

User = get_user_model()


class SpendTests(TestCase):
    def test_total_spend_includes_cancelled_fee(self):
        member = User(phone='13800000001', username='13800000001', role='member')
        member.set_password('x')
        member.save()
        venue = Venue.objects.create(name='测试场馆')
        court = Court.objects.create(venue=venue, name='1号场')
        slot = TimeSlot.objects.create(venue=venue, start_time='10:00', end_time='11:00', price='100.00')
        d = timezone.localdate()
        Booking.objects.create(user=member, court=court, date=d, time_slot=slot, status='paid', amount='100.00')
        Booking.objects.create(user=member, court=court, date=d + timedelta(days=1), time_slot=slot, status='cancelled', amount='100.00', fee_amount='20.00')
        self.assertEqual(member.get_total_spend(), Decimal('120.00'))

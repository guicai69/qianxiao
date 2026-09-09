from datetime import datetime, timedelta
from decimal import Decimal
from unittest import mock
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.bookings.models import Booking
from apps.payments.models import Payment
from apps.venues.models import Venue, Court, TimeSlot

User = get_user_model()
TZ = ZoneInfo('Asia/Shanghai')


def make_user(phone, role='member', password='123456', level='normal', balance='0'):
    u = User(phone=phone, username=phone, role=role, level=level, balance=balance)
    u.set_password(password)
    u.save()
    return u


def make_venue_court_slot(price='100.00', start='10:00', end='11:00'):
    venue = Venue.objects.create(name='测试场馆', address='测试地址')
    court = Court.objects.create(venue=venue, name='1号场')
    slot = TimeSlot.objects.create(venue=venue, start_time=start, end_time=end, price=price)
    return venue, court, slot


class BookingCreateTests(APITestCase):
    def test_conflict_rejected(self):
        _, court, slot = make_venue_court_slot()
        member = make_user('13800000001')
        self.client.force_authenticate(user=member)
        date = (timezone.localdate() + timedelta(days=1)).isoformat()
        payload = {'court': court.id, 'date': date, 'time_slot': slot.id}
        self.assertEqual(self.client.post('/api/bookings/', payload).status_code, 201)
        self.assertEqual(self.client.post('/api/bookings/', payload).status_code, 400)

    def test_past_date_rejected(self):
        _, court, slot = make_venue_court_slot()
        member = make_user('13800000001')
        self.client.force_authenticate(user=member)
        past = (timezone.localdate() - timedelta(days=1)).isoformat()
        r = self.client.post('/api/bookings/', {'court': court.id, 'date': past, 'time_slot': slot.id})
        self.assertEqual(r.status_code, 400)


class CancelPolicyTests(APITestCase):
    def _paid_booking(self, member, d, start, amount='100.00'):
        _, court, slot = make_venue_court_slot(price=amount, start=start)
        return Booking.objects.create(user=member, court=court, date=d, time_slot=slot, status='paid', amount=amount)

    def test_free_cancel_full_refund(self):
        member = make_user('13800000001', balance='0')
        b = self._paid_booking(member, datetime(2025, 1, 15).date(), '14:00', amount='100.00')
        self.client.force_authenticate(user=member)
        fixed = datetime(2025, 1, 15, 10, 0, tzinfo=TZ)
        with mock.patch('django.utils.timezone.now', return_value=fixed):
            r = self.client.post(f'/api/bookings/{b.id}/cancel/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['data']['refund_amount'], '100.00')
        member.refresh_from_db()
        self.assertEqual(str(member.balance), '100.00')
        b.refresh_from_db()
        self.assertEqual(b.status, 'cancelled')
        self.assertEqual(str(b.fee_amount), '0.00')
        self.assertTrue(Payment.objects.filter(type='refund', amount='100.00').exists())

    def test_member_blocked_in_fee_window(self):
        member = make_user('13800000001', balance='0')
        b = self._paid_booking(member, datetime(2025, 1, 15).date(), '11:30', amount='100.00')
        self.client.force_authenticate(user=member)
        fixed = datetime(2025, 1, 15, 10, 0, tzinfo=TZ)
        with mock.patch('django.utils.timezone.now', return_value=fixed):
            r = self.client.post(f'/api/bookings/{b.id}/cancel/')
        self.assertEqual(r.status_code, 403)

    def test_staff_fee_window_80_percent(self):
        member = make_user('13800000001', balance='0')
        admin = make_user('13800000000', role='admin')
        b = self._paid_booking(member, datetime(2025, 1, 15).date(), '11:30', amount='100.00')
        self.client.force_authenticate(user=admin)
        fixed = datetime(2025, 1, 15, 10, 0, tzinfo=TZ)
        with mock.patch('django.utils.timezone.now', return_value=fixed):
            r = self.client.post(f'/api/bookings/{b.id}/cancel/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['data']['refund_amount'], '80.00')
        member.refresh_from_db()
        self.assertEqual(str(member.balance), '80.00')
        b.refresh_from_db()
        self.assertEqual(str(b.fee_amount), '20.00')

    def test_after_start_no_refund(self):
        member = make_user('13800000001', balance='0')
        admin = make_user('13800000000', role='admin')
        b = self._paid_booking(member, datetime(2025, 1, 15).date(), '09:00', amount='100.00')
        self.client.force_authenticate(user=admin)
        fixed = datetime(2025, 1, 15, 10, 0, tzinfo=TZ)
        with mock.patch('django.utils.timezone.now', return_value=fixed):
            r = self.client.post(f'/api/bookings/{b.id}/cancel/')
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(r.data.get('data', {}).get('refund_amount'))
        member.refresh_from_db()
        self.assertEqual(str(member.balance), '0.00')
        b.refresh_from_db()
        self.assertEqual(str(b.fee_amount), '100.00')


class CheckInTests(APITestCase):
    def test_check_in_wrong_date_rejected(self):
        member = make_user('13800000001')
        admin = make_user('13800000000', role='admin')
        _, court, slot = make_venue_court_slot()
        tomorrow = timezone.localdate() + timedelta(days=1)
        b = Booking.objects.create(user=member, court=court, date=tomorrow, time_slot=slot, status='paid', amount='100.00')
        self.client.force_authenticate(user=admin)
        r = self.client.post(f'/api/bookings/{b.id}/check_in/')
        self.assertEqual(r.status_code, 400)

    def test_check_in_today_ok(self):
        member = make_user('13800000001')
        admin = make_user('13800000000', role='admin')
        _, court, slot = make_venue_court_slot()
        today = timezone.localdate()
        b = Booking.objects.create(user=member, court=court, date=today, time_slot=slot, status='paid', amount='100.00')
        self.client.force_authenticate(user=admin)
        r = self.client.post(f'/api/bookings/{b.id}/check_in/')
        self.assertEqual(r.status_code, 200)


class ExpiryCommandTests(APITestCase):
    def test_command_cancels_stale_pendings(self):
        member = make_user('13800000001')
        _, court, slot = make_venue_court_slot()
        tomorrow = timezone.localdate() + timedelta(days=1)
        b = Booking.objects.create(user=member, court=court, date=tomorrow, time_slot=slot, status='pending', amount='100.00')
        Booking.objects.filter(pk=b.pk).update(created_at=timezone.now() - timedelta(minutes=20))
        call_command('cancel_expired_bookings')
        b.refresh_from_db()
        self.assertEqual(b.status, 'cancelled')


class PendingTimeoutTests(APITestCase):
    def test_stale_pending_is_freed(self):
        member = make_user('13800000001')
        member2 = make_user('13800000002')
        venue, court, slot = make_venue_court_slot()
        tomorrow = timezone.localdate() + timedelta(days=1)
        b = Booking.objects.create(user=member, court=court, date=tomorrow, time_slot=slot, status='pending', amount='100.00')
        Booking.objects.filter(pk=b.pk).update(created_at=timezone.now() - timedelta(minutes=20))
        self.client.force_authenticate(user=member2)
        r = self.client.get(f'/api/venues/{venue.id}/availability/', {'date': tomorrow.isoformat()})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['occupied'], [])
        b.refresh_from_db()
        self.assertEqual(b.status, 'cancelled')

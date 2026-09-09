from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.bookings.models import Booking
from apps.payments.models import Payment
from apps.venues.models import Venue, Court, TimeSlot

User = get_user_model()


def make_user(phone, role='member', password='123456', level='normal', balance='0'):
    u = User(phone=phone, username=phone, role=role, level=level, balance=balance)
    u.set_password(password)
    u.save()
    return u


def make_venue_court_slot(price='100.00'):
    venue = Venue.objects.create(name='测试场馆')
    court = Court.objects.create(venue=venue, name='1号场')
    slot = TimeSlot.objects.create(venue=venue, start_time='10:00', end_time='11:00', price=price)
    return venue, court, slot


class ConfirmCashTests(APITestCase):
    def test_confirm_cash_creates_payment(self):
        member = make_user('13800000001')
        admin = make_user('13800000000', role='admin')
        _, court, slot = make_venue_court_slot(price='100.00')
        tomorrow = timezone.localdate() + timedelta(days=1)
        b = Booking.objects.create(user=member, court=court, date=tomorrow, time_slot=slot, status='pending', amount='100.00')
        self.client.force_authenticate(user=admin)
        r = self.client.post('/api/payments/confirm_cash/', {'booking_id': b.id})
        self.assertEqual(r.status_code, 200)
        b.refresh_from_db()
        self.assertEqual(b.status, 'paid')
        self.assertTrue(Payment.objects.filter(booking=b, type='booking', method='cash').exists())

    def test_confirm_cash_requires_staff(self):
        member = make_user('13800000001')
        _, court, slot = make_venue_court_slot()
        tomorrow = timezone.localdate() + timedelta(days=1)
        b = Booking.objects.create(user=member, court=court, date=tomorrow, time_slot=slot, status='pending', amount='100.00')
        self.client.force_authenticate(user=member)
        r = self.client.post('/api/payments/confirm_cash/', {'booking_id': b.id})
        self.assertEqual(r.status_code, 403)


class RechargeMethodTests(APITestCase):
    def test_balance_recharge_rejected(self):
        member = make_user('13800000001')
        self.client.force_authenticate(user=member)
        r = self.client.post('/api/payments/recharge/', {'amount': '100', 'method': 'balance'})
        self.assertEqual(r.status_code, 400)


class PaymentIsolationTests(APITestCase):
    def test_member_list_shows_only_own_payments(self):
        a = make_user('13800000001')
        b = make_user('13800000002')
        Payment.objects.create(user=a, type='recharge', amount='100.00', method='wechat', status='success')
        Payment.objects.create(user=b, type='recharge', amount='50.00', method='wechat', status='success')
        self.client.force_authenticate(user=a)
        r = self.client.get('/api/payments/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 1)
        self.assertEqual(r.data['results'][0]['amount'], '100.00')
        self.assertEqual(r.data['results'][0]['user_phone'], '13800000001')


class PayTimeoutTests(APITestCase):
    def test_stale_pending_pay_rejected(self):
        member = make_user('13800000001', balance='1000')
        _, court, slot = make_venue_court_slot(price='100.00')
        tomorrow = timezone.localdate() + timedelta(days=1)
        b = Booking.objects.create(user=member, court=court, date=tomorrow, time_slot=slot, status='pending', amount='100.00')
        Booking.objects.filter(pk=b.pk).update(created_at=timezone.now() - timedelta(minutes=20))
        self.client.force_authenticate(user=member)
        r = self.client.post('/api/payments/pay/', {'booking_id': b.id, 'method': 'balance'})
        self.assertEqual(r.status_code, 400)
        b.refresh_from_db()
        self.assertEqual(b.status, 'cancelled')

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.payments.models import Payment
from apps.venues.models import Venue, Court, TimeSlot
from apps.bookings.models import Booking

User = get_user_model()


def make_user(phone, role='member', password='123456'):
    u = User(phone=phone, username=phone, role=role)
    u.set_password(password)
    u.save()
    return u


class OverviewTests(APITestCase):
    def test_overview_includes_recharge_refund_bonus(self):
        member = make_user('13800000001')
        admin = make_user('13800000000', role='admin')
        Payment.objects.create(user=member, type='recharge', amount='100.00', bonus='10.00', method='wechat', status='success')
        Payment.objects.create(user=member, type='refund', amount='20.00', method='balance', status='success')
        self.client.force_authenticate(user=admin)
        r = self.client.get('/api/stats/overview/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['total_recharge'], 100.0)
        self.assertEqual(r.data['total_bonus'], 10.0)
        self.assertEqual(r.data['total_refund'], 20.0)

    def test_member_forbidden(self):
        member = make_user('13800000001')
        self.client.force_authenticate(user=member)
        r = self.client.get('/api/stats/overview/')
        self.assertEqual(r.status_code, 403)


class TrendTests(APITestCase):
    def setUp(self):
        self.admin = make_user('13800000000', role='admin')
        self.member = make_user('13800000001')
        venue = Venue.objects.create(name='测试场馆')
        court = Court.objects.create(venue=venue, name='1号场')
        slot = TimeSlot.objects.create(venue=venue, start_time='10:00', end_time='11:00', price='100.00')
        today = timezone.localdate()
        Booking.objects.create(user=self.member, court=court, date=today, time_slot=slot, status='paid', amount='100.00')
        Booking.objects.create(user=self.member, court=court, date=today, time_slot=slot, status='pending', amount='100.00')
        Booking.objects.create(user=self.member, court=court, date=today - timedelta(days=30), time_slot=slot, status='paid', amount='50.00')
        self.client.force_authenticate(user=self.admin)

    def test_revenue_trend_only_paid_in_window(self):
        r = self.client.get('/api/stats/revenue_trend/', {'days': 7})
        self.assertEqual(r.status_code, 200)
        total = sum(d['revenue'] for d in r.data['days'])
        self.assertEqual(total, 100.0)

    def test_revenue_trend_bad_days_returns_400(self):
        r = self.client.get('/api/stats/revenue_trend/', {'days': 'abc'})
        self.assertEqual(r.status_code, 400)

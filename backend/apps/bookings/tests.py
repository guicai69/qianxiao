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

    def test_past_time_slot_today_rejected(self):
        """今天已经开场的时段不能下单（如 19:23 时 19:00-20:00 时段应被拒）"""
        _, court, slot = make_venue_court_slot(start='10:00', end='11:00')
        member = make_user('13800000001')
        self.client.force_authenticate(user=member)
        fixed = timezone.localtime().replace(hour=12, minute=0, second=0, microsecond=0)
        with mock.patch('django.utils.timezone.now', return_value=fixed):
            r = self.client.post('/api/bookings/', {
                'court': court.id, 'date': fixed.date().isoformat(), 'time_slot': slot.id,
            })
        self.assertEqual(r.status_code, 400)

    def test_future_time_slot_today_allowed(self):
        """今天还没开场的时段照常可约"""
        _, court, slot = make_venue_court_slot(start='18:00', end='19:00')
        member = make_user('13800000001')
        self.client.force_authenticate(user=member)
        fixed = timezone.localtime().replace(hour=12, minute=0, second=0, microsecond=0)
        with mock.patch('django.utils.timezone.now', return_value=fixed):
            r = self.client.post('/api/bookings/', {
                'court': court.id, 'date': fixed.date().isoformat(), 'time_slot': slot.id,
            })
        self.assertEqual(r.status_code, 201)

    def test_past_date_rejected(self):
        _, court, slot = make_venue_court_slot()
        member = make_user('13800000001')
        self.client.force_authenticate(user=member)
        past = (timezone.localdate() - timedelta(days=1)).isoformat()
        r = self.client.post('/api/bookings/', {'court': court.id, 'date': past, 'time_slot': slot.id})
        self.assertEqual(r.status_code, 400)

    def test_cross_venue_booking_rejected(self):
        _, court, _ = make_venue_court_slot()
        other_venue = Venue.objects.create(name='另一场馆')
        other_slot = TimeSlot.objects.create(
            venue=other_venue, start_time='10:00', end_time='11:00', price='100.00',
        )
        member = make_user('13800000001')
        self.client.force_authenticate(user=member)
        date = (timezone.localdate() + timedelta(days=1)).isoformat()
        r = self.client.post('/api/bookings/', {
            'court': court.id, 'date': date, 'time_slot': other_slot.id,
        })
        self.assertEqual(r.status_code, 400)

    def test_invalid_list_filters_return_400(self):
        member = make_user('13800000001')
        self.client.force_authenticate(user=member)
        self.assertEqual(self.client.get('/api/bookings/', {'date': 'abc'}).status_code, 400)
        self.assertEqual(self.client.get('/api/bookings/', {'venue': 'abc'}).status_code, 400)
        self.assertEqual(self.client.get('/api/bookings/', {'status': 'nope'}).status_code, 400)


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

    def test_double_cancel_refunds_once(self):
        member = make_user('13800000001', balance='0')
        d = timezone.localdate() + timedelta(days=3)
        b = self._paid_booking(member, d, '14:00', amount='100.00')
        self.client.force_authenticate(user=member)
        fixed = datetime.combine(timezone.localdate(), datetime.min.time(), tzinfo=TZ)
        with mock.patch('django.utils.timezone.now', return_value=fixed):
            self.assertEqual(self.client.post(f'/api/bookings/{b.id}/cancel/').status_code, 200)
            self.assertEqual(self.client.post(f'/api/bookings/{b.id}/cancel/').status_code, 400)
        member.refresh_from_db()
        self.assertEqual(str(member.balance), '100.00')
        self.assertEqual(Payment.objects.filter(type='refund').count(), 1)

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


class PayCancelRefundTests(APITestCase):
    """回归：支付后取消必须把余额退回（用户报过「取消只提示已取消、钱没退」）"""

    def test_pay_then_cancel_refunds_balance(self):
        member = make_user('13800000001', balance='1000.00')
        _, court, slot = make_venue_court_slot(price='100.00')
        tomorrow = timezone.localdate() + timedelta(days=1)
        b = Booking.objects.create(
            user=member, court=court, date=tomorrow, time_slot=slot,
            status='pending', amount='100.00',
        )
        self.client.force_authenticate(user=member)

        r = self.client.post('/api/payments/pay/', {'booking_id': b.id, 'method': 'balance'})
        self.assertEqual(r.status_code, 200)
        member.refresh_from_db()
        self.assertEqual(str(member.balance), '900.00')

        r2 = self.client.post(f'/api/bookings/{b.id}/cancel/')
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.data['data']['refund_amount'], '100.00')
        member.refresh_from_db()
        self.assertEqual(str(member.balance), '1000.00')
        self.assertTrue(Payment.objects.filter(booking=b, type='refund', amount='100.00').exists())

    def test_celery_task_cancels_stale_pendings(self):
        member = make_user('13800000001')
        _, court, slot = make_venue_court_slot()
        tomorrow = timezone.localdate() + timedelta(days=1)
        b = Booking.objects.create(user=member, court=court, date=tomorrow, time_slot=slot, status='pending', amount='100.00')
        Booking.objects.filter(pk=b.pk).update(created_at=timezone.now() - timedelta(minutes=20))
        from apps.bookings.tasks import cancel_expired_bookings_task
        cancelled = cancel_expired_bookings_task.run()
        self.assertEqual(cancelled, 1)
        b.refresh_from_db()
        self.assertEqual(b.status, 'cancelled')


class PendingTimeoutTests(APITestCase):
    def test_availability_releases_expired_pending_without_write(self):
        """超时未支付的订单在可约时段里视为已释放，但 GET 本身不写库"""
        member = make_user('13800000001')
        member2 = make_user('13800000002')
        venue, court, slot = make_venue_court_slot()
        tomorrow = timezone.localdate() + timedelta(days=1)
        b = Booking.objects.create(user=member, court=court, date=tomorrow, time_slot=slot, status='pending', amount='100.00')
        Booking.objects.filter(pk=b.pk).update(created_at=timezone.now() - timedelta(minutes=20))
        self.client.force_authenticate(user=member2)
        r = self.client.get(f'/api/venues/{venue.id}/availability/', {'date': tomorrow.isoformat()})
        self.assertEqual(r.status_code, 200)
        # 过期未支付 = 没有真正占住时段，列表里不应再出现
        self.assertEqual(r.data['occupied'], [])
        # GET 无写副作用：状态落库交给 cancel_expired_bookings 定时任务
        b.refresh_from_db()
        self.assertEqual(b.status, 'pending')

    def test_my_orders_cancels_stale_pending(self):
        """我的订单列表会把超时未支付的订单落库取消，待支付页签不再出现僵尸单"""
        member = make_user('13800000001')
        _, court, slot = make_venue_court_slot()
        tomorrow = timezone.localdate() + timedelta(days=1)
        b = Booking.objects.create(
            user=member, court=court, date=tomorrow, time_slot=slot,
            status='pending', amount='100.00',
        )
        Booking.objects.filter(pk=b.pk).update(created_at=timezone.now() - timedelta(minutes=20))
        self.client.force_authenticate(user=member)
        r = self.client.get('/api/bookings/my/')
        self.assertEqual(r.status_code, 200)
        b.refresh_from_db()
        self.assertEqual(b.status, 'cancelled')
        # 返回的列表里这条已经是「已取消」，不再是待支付
        row = [x for x in r.data['results'] if x['id'] == b.id][0]
        self.assertEqual(row['status'], 'cancelled')
        # 待支付页签里不会再出现
        r = self.client.get('/api/bookings/', {'status': 'pending'})
        self.assertNotIn(b.id, [x['id'] for x in r.data['results']])

    def test_availability_keeps_fresh_pending(self):
        """还在支付时限内的待支付订单照常占用时段"""
        member = make_user('13800000001')
        member2 = make_user('13800000002')
        venue, court, slot = make_venue_court_slot()
        tomorrow = timezone.localdate() + timedelta(days=1)
        Booking.objects.create(user=member, court=court, date=tomorrow, time_slot=slot, status='pending', amount='100.00')
        self.client.force_authenticate(user=member2)
        r = self.client.get(f'/api/venues/{venue.id}/availability/', {'date': tomorrow.isoformat()})
        self.assertEqual(r.data['occupied'], [{'court_id': court.id, 'time_slot_id': slot.id}])


class OrderClosedStateTests(APITestCase):
    """到期/逾期的未完成订单视作结束：已支付但时段已过、待支付但超时未付"""

    def setUp(self):
        self.member = make_user('13800000001')
        self.client.force_authenticate(user=self.member)

    def test_paid_booking_finished_after_slot_end(self):
        _, court, slot = make_venue_court_slot()
        yesterday = timezone.localdate() - timedelta(days=1)
        b = Booking.objects.create(
            user=self.member, court=court, date=yesterday, time_slot=slot,
            status='paid', amount='100.00',
        )
        r = self.client.get(f'/api/bookings/{b.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data['is_finished'])
        self.assertFalse(r.data['is_expired'])

    def test_paid_booking_tomorrow_not_finished(self):
        _, court, slot = make_venue_court_slot()
        tomorrow = timezone.localdate() + timedelta(days=1)
        b = Booking.objects.create(
            user=self.member, court=court, date=tomorrow, time_slot=slot,
            status='paid', amount='100.00',
        )
        r = self.client.get(f'/api/bookings/{b.id}/')
        self.assertFalse(r.data['is_finished'])

    def test_expired_pending_flagged_on_list(self):
        _, court, slot = make_venue_court_slot()
        tomorrow = timezone.localdate() + timedelta(days=1)
        b = Booking.objects.create(
            user=self.member, court=court, date=tomorrow, time_slot=slot,
            status='pending', amount='100.00',
        )
        Booking.objects.filter(pk=b.pk).update(created_at=timezone.now() - timedelta(minutes=20))
        r = self.client.get('/api/bookings/', {'status': 'pending'})
        self.assertEqual(r.status_code, 200)
        row = [x for x in r.data['results'] if x['id'] == b.id][0]
        self.assertTrue(row['is_expired'])
        self.assertFalse(row['is_finished'])

    def test_fresh_pending_not_expired(self):
        _, court, slot = make_venue_court_slot()
        tomorrow = timezone.localdate() + timedelta(days=1)
        b = Booking.objects.create(
            user=self.member, court=court, date=tomorrow, time_slot=slot,
            status='pending', amount='100.00',
        )
        r = self.client.get(f'/api/bookings/{b.id}/')
        self.assertFalse(r.data['is_expired'])

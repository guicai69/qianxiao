from datetime import datetime, timedelta
from unittest import mock
from zoneinfo import ZoneInfo

from django.utils import timezone
from rest_framework.test import APITestCase

from apps.bookings.models import Booking, CancellationRequest
from apps.bookings.tests import make_user, make_venue_court_slot
from apps.bookings.utils import process_due_refunds

TZ = ZoneInfo('Asia/Shanghai')


def _paid_booking(member, start='11:30', amount='100.00'):
    _, court, slot = make_venue_court_slot(price=amount, start=start, end='23:00')
    return Booking.objects.create(
        user=member, court=court, date=datetime(2025, 1, 15).date(),
        time_slot=slot, status='paid', amount=amount,
    )


FIXED = datetime(2025, 1, 15, 10, 0, tzinfo=TZ)


class CancellationRequestTests(APITestCase):
    def test_member_request_within_2h(self):
        member = make_user('13800000001')
        b = _paid_booking(member, start='11:30')
        self.client.force_authenticate(user=member)
        with mock.patch('django.utils.timezone.now', return_value=FIXED):
            r = self.client.post(f'/api/bookings/{b.id}/request_cancel/', {'reason': '临时有事'})
        self.assertEqual(r.status_code, 200)
        req = CancellationRequest.objects.get(booking=b)
        self.assertEqual(req.status, 'pending')
        self.assertEqual(str(req.refund_amount), '100.00')

    def test_member_request_over_2h_rejected(self):
        member = make_user('13800000001')
        b = _paid_booking(member, start='14:00')
        self.client.force_authenticate(user=member)
        with mock.patch('django.utils.timezone.now', return_value=FIXED):
            r = self.client.post(f'/api/bookings/{b.id}/request_cancel/', {})
        self.assertEqual(r.status_code, 400)

    def test_after_start_rejected(self):
        member = make_user('13800000001')
        b = _paid_booking(member, start='09:00')
        self.client.force_authenticate(user=member)
        with mock.patch('django.utils.timezone.now', return_value=FIXED):
            r = self.client.post(f'/api/bookings/{b.id}/request_cancel/', {})
        self.assertEqual(r.status_code, 400)

    def test_not_paid_rejected(self):
        member = make_user('13800000001')
        _, court, slot = make_venue_court_slot(start='11:30', end='23:00')
        b = Booking.objects.create(
            user=member, court=court, date=datetime(2025, 1, 15).date(),
            time_slot=slot, status='pending', amount='100.00',
        )
        self.client.force_authenticate(user=member)
        with mock.patch('django.utils.timezone.now', return_value=FIXED):
            r = self.client.post(f'/api/bookings/{b.id}/request_cancel/', {})
        self.assertEqual(r.status_code, 400)

    def test_duplicate_request_rejected(self):
        member = make_user('13800000001')
        b = _paid_booking(member, start='11:30')
        CancellationRequest.objects.create(booking=b, user=member, refund_amount='100.00', status='pending')
        self.client.force_authenticate(user=member)
        with mock.patch('django.utils.timezone.now', return_value=FIXED):
            r = self.client.post(f'/api/bookings/{b.id}/request_cancel/', {})
        self.assertEqual(r.status_code, 400)


class ApproveRejectTests(APITestCase):
    def _setup(self):
        member = make_user('13800000001')
        _, court, slot = make_venue_court_slot()
        b = Booking.objects.create(
            user=member, court=court, date=timezone.localdate() + timedelta(days=1),
            time_slot=slot, status='paid', amount='100.00',
        )
        req = CancellationRequest.objects.create(
            booking=b, user=member, refund_amount='100.00', status='pending',
        )
        return member, b, req

    def test_member_cannot_approve(self):
        member, b, req = self._setup()
        self.client.force_authenticate(user=member)
        r = self.client.post(f'/api/cancellation-requests/{req.id}/approve/')
        self.assertEqual(r.status_code, 403)

    def test_approve_sets_refund_at_5min(self):
        member, b, req = self._setup()
        reception = make_user('13900000001', role='reception')
        self.client.force_authenticate(user=reception)
        r = self.client.post(f'/api/cancellation-requests/{req.id}/approve/')
        self.assertEqual(r.status_code, 200)
        req.refresh_from_db()
        self.assertEqual(req.status, 'approved')
        self.assertIsNotNone(req.refund_at)
        self.assertAlmostEqual((req.refund_at - req.reviewed_at).total_seconds(), 300, delta=2)

    def test_reject(self):
        member, b, req = self._setup()
        reception = make_user('13900000001', role='reception')
        self.client.force_authenticate(user=reception)
        r = self.client.post(f'/api/cancellation-requests/{req.id}/reject/', {'reject_reason': '时间太紧'})
        self.assertEqual(r.status_code, 200)
        req.refresh_from_db()
        self.assertEqual(req.status, 'rejected')
        self.assertEqual(req.reject_reason, '时间太紧')


class ProcessDueRefundsTests(APITestCase):
    def test_due_refund_processes(self):
        member = make_user('13800000001')  # 模拟已支付后余额为 0
        _, court, slot = make_venue_court_slot(price='100.00')
        b = Booking.objects.create(
            user=member, court=court, date=timezone.localdate() + timedelta(days=1),
            time_slot=slot, status='paid', amount='100.00',
        )
        now = timezone.now()
        CancellationRequest.objects.create(
            booking=b, user=member, refund_amount='100.00', status='approved',
            reviewed_at=now - timedelta(minutes=6), refund_at=now - timedelta(minutes=1),
        )
        count = process_due_refunds()
        self.assertEqual(count, 1)
        member.refresh_from_db()
        self.assertEqual(str(member.balance), '100.00')
        b.refresh_from_db()
        self.assertEqual(b.status, 'cancelled')
        self.assertEqual(
            CancellationRequest.objects.get(booking=b).status, 'refunded',
        )

    def test_not_due_yet_not_processed(self):
        member = make_user('13800000001')
        _, court, slot = make_venue_court_slot(price='100.00')
        b = Booking.objects.create(
            user=member, court=court, date=timezone.localdate() + timedelta(days=1),
            time_slot=slot, status='paid', amount='100.00',
        )
        CancellationRequest.objects.create(
            booking=b, user=member, refund_amount='100.00', status='approved',
            refund_at=timezone.now() + timedelta(minutes=3),
        )
        self.assertEqual(process_due_refunds(), 0)
        b.refresh_from_db()
        self.assertEqual(b.status, 'paid')

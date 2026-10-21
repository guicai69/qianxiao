from datetime import datetime, timedelta
from unittest import mock
from zoneinfo import ZoneInfo

from django.utils import timezone
from rest_framework.test import APITestCase

from apps.bookings.models import Booking, CancellationRequest
from apps.bookings.tests import make_user, make_venue_court_slot
from apps.bookings.utils import process_cancellation_requests
from apps.payments.models import Payment

TZ = ZoneInfo('Asia/Shanghai')


def _paid_booking(member, start='11:30', end='23:00', amount='100.00', checked_in=False):
    _, court, slot = make_venue_court_slot(price=amount, start=start, end=end)
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

    def test_member_request_over_2h_allowed(self):
        """已支付订单距开场超过 2 小时也能申请退场（前台审批）"""
        member = make_user('13800000001')
        b = _paid_booking(member, start='14:00')
        self.client.force_authenticate(user=member)
        with mock.patch('django.utils.timezone.now', return_value=FIXED):
            r = self.client.post(f'/api/bookings/{b.id}/request_cancel/', {'reason': '临时有事'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(CancellationRequest.objects.get(booking=b).status, 'pending')

    def test_after_start_but_before_end_allowed(self):
        """已开场但时段未结束：仍可申请退场（前台审批决定是否退款）"""
        member = make_user('13800000001')
        b = _paid_booking(member, start='09:00', end='23:00')
        self.client.force_authenticate(user=member)
        with mock.patch('django.utils.timezone.now', return_value=FIXED):
            r = self.client.post(f'/api/bookings/{b.id}/request_cancel/', {})
        self.assertEqual(r.status_code, 200)

    def test_after_end_rejected(self):
        member = make_user('13800000001')
        b = _paid_booking(member, start='09:00', end='09:30')
        self.client.force_authenticate(user=member)
        with mock.patch('django.utils.timezone.now', return_value=FIXED):
            r = self.client.post(f'/api/bookings/{b.id}/request_cancel/', {})
        self.assertEqual(r.status_code, 400)

    def test_checked_in_rejected(self):
        member = make_user('13800000001')
        b = _paid_booking(member, start='11:30')
        b.checked_in = True
        b.save(update_fields=['checked_in'])
        self.client.force_authenticate(user=member)
        with mock.patch('django.utils.timezone.now', return_value=FIXED):
            r = self.client.post(f'/api/bookings/{b.id}/request_cancel/', {})
        self.assertEqual(r.status_code, 400)

    def test_member_cannot_self_cancel_while_request_pending(self):
        """有未完成退场申请时，会员不能再自助取消，避免二次退款"""
        member = make_user('13800000001')
        b = _paid_booking(member, start='14:00')
        CancellationRequest.objects.create(
            booking=b, user=member, refund_amount='100.00', status='pending',
        )
        self.client.force_authenticate(user=member)
        with mock.patch('django.utils.timezone.now', return_value=FIXED):
            r = self.client.post(f'/api/bookings/{b.id}/cancel/')
        self.assertEqual(r.status_code, 400)
        b.refresh_from_db()
        self.assertEqual(b.status, 'paid')

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

    def test_approve_refunds_immediately(self):
        """通过申请后立刻退款：余额入账、订单取消、申请置已退款"""
        member, b, req = self._setup()
        reception = make_user('13900000001', role='reception')
        self.client.force_authenticate(user=reception)
        r = self.client.post(f'/api/cancellation-requests/{req.id}/approve/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('已退款', r.data['message'])

        req.refresh_from_db()
        self.assertEqual(req.status, 'refunded')
        self.assertEqual(req.reviewed_by_id, reception.id)
        self.assertIsNotNone(req.reviewed_at)
        self.assertIsNotNone(req.refunded_at)

        member.refresh_from_db()
        self.assertEqual(str(member.balance), '100.00')
        b.refresh_from_db()
        self.assertEqual(b.status, 'cancelled')
        self.assertTrue(
            Payment.objects.filter(booking=b, type='refund', amount='100.00').exists()
        )

    def test_approve_zero_refund_still_cancels_booking(self):
        """应退金额为 0（手续费全扣）时只取消订单，不产生退款流水"""
        member, b, req = self._setup()
        req.refund_amount = '0.00'
        req.fee_amount = '100.00'
        req.save(update_fields=['refund_amount', 'fee_amount'])
        reception = make_user('13900000001', role='reception')
        self.client.force_authenticate(user=reception)
        r = self.client.post(f'/api/cancellation-requests/{req.id}/approve/')
        self.assertEqual(r.status_code, 200)
        b.refresh_from_db()
        self.assertEqual(b.status, 'cancelled')
        self.assertEqual(str(b.fee_amount), '100.00')
        self.assertFalse(Payment.objects.filter(booking=b, type='refund').exists())
        self.assertEqual(CancellationRequest.objects.get(pk=req.pk).status, 'refunded')

    def test_reject(self):
        member, b, req = self._setup()
        reception = make_user('13900000001', role='reception')
        self.client.force_authenticate(user=reception)
        r = self.client.post(f'/api/cancellation-requests/{req.id}/reject/', {'reject_reason': '时间太紧'})
        self.assertEqual(r.status_code, 200)
        req.refresh_from_db()
        self.assertEqual(req.status, 'rejected')
        self.assertEqual(req.reject_reason, '时间太紧')


class AutoApproveAndRefundTests(APITestCase):
    """超过 5 分钟没人处理的退场申请：自动通过并退款"""

    def _paid_and_request(self, age_minutes):
        member = make_user('13800000001')  # 模拟已支付后余额为 0
        _, court, slot = make_venue_court_slot(price='100.00')
        b = Booking.objects.create(
            user=member, court=court, date=timezone.localdate() + timedelta(days=1),
            time_slot=slot, status='paid', amount='100.00',
        )
        req = CancellationRequest.objects.create(
            booking=b, user=member, refund_amount='100.00', status='pending',
        )
        # created_at 是 auto_now_add：测试里直接改写成「N 分钟前提交」
        CancellationRequest.objects.filter(pk=req.pk).update(
            created_at=timezone.now() - timedelta(minutes=age_minutes),
        )
        return member, b, req

    def test_stale_pending_auto_approved_and_refunded(self):
        member, b, req = self._paid_and_request(age_minutes=6)
        self.assertEqual(process_cancellation_requests(), 1)
        req.refresh_from_db()
        self.assertEqual(req.status, 'refunded')
        self.assertIsNone(req.reviewed_by_id)  # 系统自动通过，无审批人
        self.assertIsNotNone(req.reviewed_at)
        self.assertIsNotNone(req.refunded_at)
        member.refresh_from_db()
        self.assertEqual(str(member.balance), '100.00')
        b.refresh_from_db()
        self.assertEqual(b.status, 'cancelled')

    def test_recent_pending_left_alone(self):
        member, b, req = self._paid_and_request(age_minutes=1)
        self.assertEqual(process_cancellation_requests(), 0)
        self.assertEqual(CancellationRequest.objects.get(pk=req.pk).status, 'pending')
        b.refresh_from_db()
        self.assertEqual(b.status, 'paid')

    def test_approved_request_refunded_right_away(self):
        """历史遗留的「已通过待退款」申请：不再等 refund_at，直接结算"""
        member, b, req = self._paid_and_request(age_minutes=1)
        CancellationRequest.objects.filter(pk=req.pk).update(
            status='approved', refund_at=timezone.now() + timedelta(minutes=3),
        )
        self.assertEqual(process_cancellation_requests(), 1)
        b.refresh_from_db()
        self.assertEqual(b.status, 'cancelled')

    def test_list_endpoint_triggers_auto_approve(self):
        """打开退场申请列表时惰性触发，不必等 Celery beat"""
        member, b, req = self._paid_and_request(age_minutes=6)
        self.client.force_authenticate(user=member)
        r = self.client.get('/api/cancellation-requests/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(CancellationRequest.objects.get(pk=req.pk).status, 'refunded')

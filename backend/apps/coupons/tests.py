from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.bookings.models import Booking
from apps.coupons.models import Coupon, UserCoupon
from apps.venues.models import Venue, Court, TimeSlot

User = get_user_model()


def make_user(phone, role='member', password='123456', balance='1000.00', points=0):
    u = User(phone=phone, username=phone, role=role, balance=balance, points=points)
    u.set_password(password)
    u.save()
    return u


def make_venue_court_slot(price='100.00'):
    venue = Venue.objects.create(name='测试场馆')
    court = Court.objects.create(venue=venue, name='1号场')
    slot = TimeSlot.objects.create(venue=venue, start_time='10:00', end_time='11:00', price=price)
    return venue, court, slot


def make_coupon(amount='20.00', min_amount='50.00', total=10, claimed=0, days=7, is_active=True):
    return Coupon.objects.create(
        name='测试券', amount=amount, min_amount=min_amount, total=total, claimed=claimed,
        expires_at=timezone.now() + timedelta(days=days), is_active=is_active,
    )


class ClaimTests(APITestCase):
    def setUp(self):
        self.member = make_user('13800000001')
        self.client.force_authenticate(user=self.member)

    def test_claim_success(self):
        c = make_coupon()
        r = self.client.post(f'/api/coupons/{c.id}/claim/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(UserCoupon.objects.filter(user=self.member, coupon=c).count(), 1)

    def test_claim_exhausted(self):
        c = make_coupon(total=1, claimed=1)
        r = self.client.post(f'/api/coupons/{c.id}/claim/')
        self.assertEqual(r.status_code, 400)

    def test_claim_expired(self):
        c = make_coupon(days=-1)
        r = self.client.post(f'/api/coupons/{c.id}/claim/')
        self.assertEqual(r.status_code, 400)

    def test_claim_twice_rejected(self):
        c = make_coupon()
        self.assertEqual(self.client.post(f'/api/coupons/{c.id}/claim/').status_code, 200)
        r = self.client.post(f'/api/coupons/{c.id}/claim/')
        self.assertEqual(r.status_code, 400)

    def test_non_member_claim_rejected(self):
        admin = make_user('13800000000', role='admin')
        c = make_coupon()
        self.client.force_authenticate(user=admin)
        r = self.client.post(f'/api/coupons/{c.id}/claim/')
        self.assertEqual(r.status_code, 400)


class RedeemTests(APITestCase):
    def test_redeem_success_and_insufficient(self):
        member = make_user('13800000001', points=600)
        self.client.force_authenticate(user=member)
        r = self.client.post('/api/coupons/redeem/')
        self.assertEqual(r.status_code, 200)
        member.refresh_from_db()
        self.assertEqual(member.points, 100)
        self.assertEqual(UserCoupon.objects.filter(user=member, coupon=None).count(), 1)
        r = self.client.post('/api/coupons/redeem/')
        self.assertEqual(r.status_code, 400)


class BookingCouponTests(APITestCase):
    def setUp(self):
        self.member = make_user('13800000001', balance='1000.00')
        _, self.court, self.slot = make_venue_court_slot(price='100.00')
        self.client.force_authenticate(user=self.member)

    def test_booking_with_coupon_discount_and_pay_uses_it(self):
        c = make_coupon(amount='20.00', min_amount='50.00')
        self.client.post(f'/api/coupons/{c.id}/claim/')
        uc = UserCoupon.objects.get(user=self.member, coupon=c)
        tomorrow = (timezone.localdate() + timedelta(days=1)).isoformat()
        r = self.client.post('/api/bookings/', {
            'court': self.court.id, 'date': tomorrow, 'time_slot': self.slot.id,
            'user_coupon_id': uc.id,
        })
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['coupon_amount'], '20.00')
        self.assertEqual(r.data['amount'], '80.00')
        b = Booking.objects.get(id=r.data['id'])
        # 支付后核销
        pay = self.client.post('/api/payments/pay/', {'booking_id': b.id, 'method': 'balance'})
        self.assertEqual(pay.status_code, 200)
        uc.refresh_from_db()
        self.assertEqual(uc.status, 'used')
        self.member.refresh_from_db()
        self.assertEqual(self.member.points, 80)

    def test_booking_below_min_amount_rejected(self):
        c = make_coupon(amount='20.00', min_amount='200.00')
        self.client.post(f'/api/coupons/{c.id}/claim/')
        uc = UserCoupon.objects.get(user=self.member, coupon=c)
        tomorrow = (timezone.localdate() + timedelta(days=1)).isoformat()
        r = self.client.post('/api/bookings/', {
            'court': self.court.id, 'date': tomorrow, 'time_slot': self.slot.id,
            'user_coupon_id': uc.id,
        })
        self.assertEqual(r.status_code, 400)

    def test_pending_cancel_keeps_coupon_unused(self):
        c = make_coupon(amount='20.00')
        self.client.post(f'/api/coupons/{c.id}/claim/')
        uc = UserCoupon.objects.get(user=self.member, coupon=c)
        tomorrow = (timezone.localdate() + timedelta(days=1)).isoformat()
        r = self.client.post('/api/bookings/', {
            'court': self.court.id, 'date': tomorrow, 'time_slot': self.slot.id,
            'user_coupon_id': uc.id,
        })
        b = Booking.objects.get(id=r.data['id'])
        cancel = self.client.post(f'/api/bookings/{b.id}/cancel/')
        self.assertEqual(cancel.status_code, 200)
        uc.refresh_from_db()
        self.assertEqual(uc.status, 'unused')


class CouponAdminTests(APITestCase):
    def test_member_cannot_update(self):
        c = make_coupon()
        self.client.force_authenticate(user=make_user('13800000001'))
        r = self.client.patch(f'/api/coupons/{c.id}/', {'name': 'hack'})
        self.assertEqual(r.status_code, 403)

    def test_toggle_active(self):
        c = make_coupon(is_active=True)
        self.client.force_authenticate(user=make_user('13800000000', role='admin'))
        r = self.client.post(f'/api/coupons/{c.id}/toggle_active/')
        self.assertEqual(r.status_code, 200)
        c.refresh_from_db()
        self.assertEqual(c.is_active, False)

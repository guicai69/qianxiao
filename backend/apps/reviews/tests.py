from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.bookings.models import Booking
from apps.reviews.models import Review, Favorite, Feedback
from apps.venues.models import Venue, Court, TimeSlot

User = get_user_model()


def make_user(phone, role='member', password='123456'):
    u = User(phone=phone, username=phone, role=role)
    u.set_password(password)
    u.save()
    return u


def make_paid_checked_booking(member, checked_in=True):
    venue = Venue.objects.create(name='测试场馆')
    court = Court.objects.create(venue=venue, name='1号场')
    slot = TimeSlot.objects.create(venue=venue, start_time='10:00', end_time='11:00', price='100.00')
    b = Booking.objects.create(
        user=member, court=court, date=timezone.localdate(), time_slot=slot,
        status='paid', amount='100.00', checked_in=checked_in,
        checked_in_at=timezone.now() if checked_in else None,
    )
    return b, venue


class ReviewTests(APITestCase):
    def setUp(self):
        self.member = make_user('13800000001')
        self.client.force_authenticate(user=self.member)

    def test_review_requires_paid_and_checked_in(self):
        b, _ = make_paid_checked_booking(self.member, checked_in=False)
        r = self.client.post('/api/reviews/', {'booking': b.id, 'rating': 5, 'content': '不错'})
        self.assertEqual(r.status_code, 400)

    def test_review_success_and_duplicate_rejected(self):
        b, _ = make_paid_checked_booking(self.member)
        r = self.client.post('/api/reviews/', {'booking': b.id, 'rating': 5, 'content': '不错'})
        self.assertEqual(r.status_code, 201)
        r = self.client.post('/api/reviews/', {'booking': b.id, 'rating': 4, 'content': '再来一次'})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Review.objects.count(), 1)

    def test_review_own_booking_only(self):
        other = make_user('13800000002')
        b, _ = make_paid_checked_booking(other)
        r = self.client.post('/api/reviews/', {'booking': b.id, 'rating': 5})
        self.assertEqual(r.status_code, 403)

    def test_reply_staff_only(self):
        b, _ = make_paid_checked_booking(self.member)
        review = Review.objects.create(booking=b, user=self.member, rating=5)
        r = self.client.post(f'/api/reviews/{review.id}/reply/', {'reply': '谢谢'})
        self.assertEqual(r.status_code, 403)
        admin = make_user('13800000000', role='admin')
        self.client.force_authenticate(user=admin)
        r = self.client.post(f'/api/reviews/{review.id}/reply/', {'reply': '谢谢惠顾'})
        self.assertEqual(r.status_code, 200)
        review.refresh_from_db()
        self.assertEqual(review.reply, '谢谢惠顾')


class FavoriteTests(APITestCase):
    def test_favorite_idempotent(self):
        member = make_user('13800000001')
        _, venue = make_paid_checked_booking(member)
        self.client.force_authenticate(user=member)
        r = self.client.post('/api/favorites/', {'venue': venue.id})
        self.assertEqual(r.status_code, 201)
        r = self.client.post('/api/favorites/', {'venue': venue.id})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Favorite.objects.count(), 1)


class FeedbackTests(APITestCase):
    def test_member_create_and_staff_process(self):
        member = make_user('13800000001')
        self.client.force_authenticate(user=member)
        r = self.client.post('/api/feedbacks/', {'content': '希望延长营业时间'})
        self.assertEqual(r.status_code, 201)
        fb = Feedback.objects.get(user=member)
        admin = make_user('13800000000', role='admin')
        self.client.force_authenticate(user=admin)
        r = self.client.post(f'/api/feedbacks/{fb.id}/process/', {'reply': '已反馈给运营'})
        self.assertEqual(r.status_code, 200)
        fb.refresh_from_db()
        self.assertEqual(fb.status, 'processed')

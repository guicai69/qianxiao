from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase as DRFAPITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.bookings.models import Booking
from apps.venues.models import Venue, Court, TimeSlot

User = get_user_model()
STRONG_PWD = 'Yq4#vBd2026'


def make_user(phone, role='member', password='pass1234'):
    u = User(phone=phone, username=phone, role=role)
    u.set_password(password)
    u.save()
    return u


def get_captcha(client):
    """测试专用：取图形验证码并从缓存读出答案"""
    r = client.get('/api/auth/captcha/')
    assert r.status_code == 200
    captcha_id = r.data['data']['captcha_id']
    code = cache.get(f'captcha:{captcha_id}')
    assert code is not None
    return captcha_id, code


class SpendTests(TestCase):
    def test_total_spend_includes_cancelled_fee(self):
        member = make_user('13800000001')
        venue = Venue.objects.create(name='测试场馆')
        court = Court.objects.create(venue=venue, name='1号场')
        slot = TimeSlot.objects.create(venue=venue, start_time='10:00', end_time='11:00', price='100.00')
        d = timezone.localdate()
        Booking.objects.create(user=member, court=court, date=d, time_slot=slot, status='paid', amount='100.00')
        Booking.objects.create(user=member, court=court, date=d + timedelta(days=1), time_slot=slot, status='cancelled', amount='100.00', fee_amount='20.00')
        self.assertEqual(member.get_total_spend(), Decimal('120.00'))


class AuthApiTests(DRFAPITestCase):
    def test_captcha_required(self):
        r = self.client.post('/api/auth/register/', {
            'phone': '13811112222', 'password': STRONG_PWD, 'password2': STRONG_PWD,
        })
        self.assertEqual(r.status_code, 400)

    def test_register_success(self):
        cid, code = get_captcha(self.client)
        r = self.client.post('/api/auth/register/', {
            'phone': '13811112222', 'password': STRONG_PWD, 'password2': STRONG_PWD,
            'nickname': '新会员', 'captcha_id': cid, 'captcha_code': code,
        })
        self.assertEqual(r.status_code, 201)
        self.assertTrue(User.objects.filter(phone='13811112222').exists())

    def test_register_bad_phone_rejected(self):
        cid, code = get_captcha(self.client)
        r = self.client.post('/api/auth/register/', {
            'phone': '123abc', 'password': STRONG_PWD, 'password2': STRONG_PWD,
            'captcha_id': cid, 'captcha_code': code,
        })
        self.assertEqual(r.status_code, 400)

    def test_register_duplicate_phone_rejected(self):
        make_user('13811112222')
        cid, code = get_captcha(self.client)
        r = self.client.post('/api/auth/register/', {
            'phone': '13811112222', 'password': STRONG_PWD, 'password2': STRONG_PWD,
            'captcha_id': cid, 'captcha_code': code,
        })
        self.assertEqual(r.status_code, 400)

    def test_login_success_and_wrong_password(self):
        make_user('13811112222', password=STRONG_PWD)
        cid, code = get_captcha(self.client)
        ok = self.client.post('/api/auth/login/', {
            'phone': '13811112222', 'password': STRONG_PWD,
            'captcha_id': cid, 'captcha_code': code,
        })
        self.assertEqual(ok.status_code, 200)
        self.assertIn('access', ok.data['data'])
        cid2, code2 = get_captcha(self.client)
        bad = self.client.post('/api/auth/login/', {
            'phone': '13811112222', 'password': 'wrong',
            'captcha_id': cid2, 'captcha_code': code2,
        })
        self.assertEqual(bad.status_code, 400)


class UserManageApiTests(DRFAPITestCase):
    def test_me_patch_nickname(self):
        member = make_user('13811112222')
        self.client.force_authenticate(user=member)
        r = self.client.patch('/api/users/me/', {'nickname': '小明'})
        self.assertEqual(r.status_code, 200)
        member.refresh_from_db()
        self.assertEqual(member.nickname, '小明')

    def test_change_password(self):
        member = make_user('13811112222', password=STRONG_PWD)
        self.client.force_authenticate(user=member)
        wrong = self.client.post('/api/auth/change-password/', {
            'old_password': 'bad', 'new_password': 'New9#pass2026', 'new_password2': 'New9#pass2026',
        })
        self.assertEqual(wrong.status_code, 400)
        ok = self.client.post('/api/auth/change-password/', {
            'old_password': STRONG_PWD, 'new_password': 'New9#pass2026', 'new_password2': 'New9#pass2026',
        })
        self.assertEqual(ok.status_code, 200)
        member.refresh_from_db()
        self.assertTrue(member.check_password('New9#pass2026'))

    def test_blacklisted_user_token_rejected(self):
        member = make_user('13811112222')
        admin = make_user('13800000000', role='admin')
        # 拉黑
        self.client.force_authenticate(user=admin)
        r = self.client.post(f'/api/users/{member.id}/blacklist/')
        self.assertEqual(r.status_code, 200)
        # 被拉黑用户的真实 JWT 请求被认证层拒绝（force_authenticate 绕过认证层，不能用）
        self.client.force_authenticate(user=None)
        token = str(RefreshToken.for_user(member).access_token)
        r = self.client.get('/api/users/me/', HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(r.status_code, 401)

    def test_delete_user_is_soft(self):
        member = make_user('13811112222')
        venue = Venue.objects.create(name='测试场馆')
        court = Court.objects.create(venue=venue, name='1号场')
        slot = TimeSlot.objects.create(venue=venue, start_time='10:00', end_time='11:00', price='100.00')
        Booking.objects.create(user=member, court=court, date=timezone.localdate(), time_slot=slot, status='paid', amount='100.00')
        admin = make_user('13800000000', role='admin')
        self.client.force_authenticate(user=admin)
        r = self.client.delete(f'/api/users/{member.id}/')
        self.assertEqual(r.status_code, 204)
        member.refresh_from_db()
        self.assertFalse(member.is_active)
        # 订单与支付记录保留
        self.assertEqual(member.bookings.count(), 1)

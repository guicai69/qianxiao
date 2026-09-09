from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.payments.models import Payment

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

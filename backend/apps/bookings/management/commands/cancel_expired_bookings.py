from django.core.management.base import BaseCommand

from apps.bookings.utils import cancel_expired_pendings


class Command(BaseCommand):
    help = '取消超过 15 分钟未支付的预约订单'

    def handle(self, *args, **options):
        count = cancel_expired_pendings()
        self.stdout.write(self.style.SUCCESS(f'已取消 {count} 个过期未支付订单'))

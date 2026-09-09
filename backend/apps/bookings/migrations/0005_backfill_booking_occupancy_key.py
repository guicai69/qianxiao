from django.db import migrations


def backfill_occupancy_key(apps, schema_editor):
    Booking = apps.get_model('bookings', 'Booking')
    seen = set()
    for b in Booking.objects.filter(status='paid').order_by('id'):
        key = f'{b.court_id}-{b.date}-{b.time_slot_id}'
        if key in seen:
            # 历史重复的已支付订单：跳过，避免违反唯一索引
            continue
        b.occupancy_key = key
        b.save(update_fields=['occupancy_key'])
        seen.add(key)


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0004_booking_fee_amount_booking_occupancy_key'),
    ]

    operations = [
        migrations.RunPython(backfill_occupancy_key, migrations.RunPython.noop),
    ]

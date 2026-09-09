from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from apps.venues.models import Venue, Court
from apps.bookings.models import Booking
from apps.payments.models import Payment
from apps.users.models import User
from apps.users.permissions import IsAdminOrReception


class StatsViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminOrReception]

    @action(detail=False, methods=["get"])
    def overview(self, request):
        today = timezone.localdate()
        today_bookings = Booking.objects.filter(date=today)
        today_revenue_agg = today_bookings.filter(status="paid").aggregate(t=Sum("amount"))["t"] or 0
        total_revenue_agg = Booking.objects.filter(status="paid").aggregate(t=Sum("amount"))["t"] or 0
        total_recharge = Payment.objects.filter(type=Payment.TYPE_RECHARGE, status=Payment.STATUS_SUCCESS).aggregate(s=Sum("amount"))["s"] or 0
        total_bonus = Payment.objects.filter(type=Payment.TYPE_RECHARGE, status=Payment.STATUS_SUCCESS).aggregate(s=Sum("bonus"))["s"] or 0
        total_refund = Payment.objects.filter(type=Payment.TYPE_REFUND, status=Payment.STATUS_SUCCESS).aggregate(s=Sum("amount"))["s"] or 0
        return Response({
            "total_venues": Venue.objects.count(),
            "total_courts": Court.objects.count(),
            "total_members": User.objects.filter(role="member").count(),
            "today_bookings": today_bookings.count(),
            "today_pending": today_bookings.filter(status="pending").count(),
            "today_paid": today_bookings.filter(status="paid").count(),
            "today_revenue": float(today_revenue_agg),
            "total_revenue": float(total_revenue_agg),
            "total_recharge": float(total_recharge),
            "total_bonus": float(total_bonus),
            "total_refund": float(total_refund),
        })

    @action(detail=False, methods=["get"])
    def revenue_trend(self, request):
        days = int(request.query_params.get("days", 7))
        since = timezone.localdate() - timedelta(days=days - 1)
        qs = (
            Booking.objects.filter(status="paid", date__gte=since)
            .values("date").annotate(revenue=Sum("amount"), bookings=Count("id"))
            .order_by("date")
        )
        return Response({
            "days": [{
                "date": str(item["date"]),
                "revenue": float(item["revenue"]),
                "bookings": item["bookings"],
            } for item in qs],
        })

    @action(detail=False, methods=["get"])
    def court_usage(self, request):
        qs = (
            Booking.objects.filter(status="paid")
            .values("court__name", "court__venue__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )
        return Response({
            "courts": [{
                "name": item["court__name"],
                "venue": item["court__venue__name"],
                "count": item["count"],
            } for item in qs],
        })

    @action(detail=False, methods=["get"])
    def popular_slots(self, request):
        qs = (
            Booking.objects.filter(status="paid")
            .values("time_slot__start_time", "time_slot__end_time")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )
        return Response({
            "slots": [{
                "start": item["time_slot__start_time"].strftime("%H:%M"),
                "end": item["time_slot__end_time"].strftime("%H:%M"),
                "label": item["time_slot__start_time"].strftime("%H:%M") + "-" + item["time_slot__end_time"].strftime("%H:%M"),
                "count": item["count"],
            } for item in qs],
        })

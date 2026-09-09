from datetime import date

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count

from .models import Venue, Court, TimeSlot
from apps.bookings.models import Booking
from apps.bookings.utils import cancel_expired_pendings
from .serializers import (
    VenueListSerializer, VenueDetailSerializer, VenueCreateSerializer, VenueUpdateSerializer,
    CourtListSerializer, CourtDetailSerializer, CourtCreateSerializer, CourtUpdateSerializer,
    TimeSlotListSerializer, TimeSlotDetailSerializer, TimeSlotCreateSerializer, TimeSlotUpdateSerializer,
)
from apps.users.permissions import IsAdmin, IsAdminOrReception


class VenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.prefetch_related('courts', 'time_slots').all()

    def get_queryset(self):
        qs = super().get_queryset()
        name = self.request.query_params.get('name')
        is_active = self.request.query_params.get('is_active')
        if name:
            qs = qs.filter(name__icontains=name)
        if is_active not in (None, ''):
            qs = qs.filter(is_active=is_active.lower() in ('true', '1'))
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return VenueListSerializer
        if self.action == 'create':
            return VenueCreateSerializer
        if self.action in ('update', 'partial_update'):
            return VenueUpdateSerializer
        return VenueDetailSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'availability'):
            return [IsAuthenticated()]
        return [IsAdminOrReception()]

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """返回指定日期被占用的时段（仅 court_id + time_slot_id，不含用户信息）"""
        venue = self.get_object()
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'detail': '缺少 date 参数'}, status=400)
        try:
            bdate = date.fromisoformat(date_str)
        except ValueError:
            return Response({'detail': 'date 参数格式错误'}, status=400)

        cancel_expired_pendings()

        qs = Booking.objects.filter(
            court__venue=venue, date=bdate,
        ).exclude(status='cancelled')
        occupied = [
            {'court_id': b.court_id, 'time_slot_id': b.time_slot_id}
            for b in qs
        ]
        return Response({'date': date_str, 'occupied': occupied})

    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        venue = self.get_object()
        venue.is_active = not venue.is_active
        venue.save(update_fields=['is_active'])
        return Response({'code': 200, 'message': '状态已更新', 'data': {'is_active': venue.is_active}})


class CourtViewSet(viewsets.ModelViewSet):
    queryset = Court.objects.select_related('venue').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return CourtListSerializer
        if self.action == 'create':
            return CourtCreateSerializer
        if self.action in ('update', 'partial_update'):
            return CourtUpdateSerializer
        return CourtDetailSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]
        if self.action == 'retrieve':
            return [IsAuthenticated()]
        return [IsAdminOrReception()]

    def get_queryset(self):
        qs = super().get_queryset()
        venue_id = self.request.query_params.get('venue')
        if venue_id:
            qs = qs.filter(venue_id=venue_id)
        return qs

    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        court = self.get_object()
        court.is_active = not court.is_active
        court.save(update_fields=['is_active'])
        return Response({'code': 200, 'message': '状态已更新', 'data': {'is_active': court.is_active}})


class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.select_related('venue').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return TimeSlotListSerializer
        if self.action == 'create':
            return TimeSlotCreateSerializer
        if self.action in ('update', 'partial_update'):
            return TimeSlotUpdateSerializer
        return TimeSlotDetailSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]
        if self.action == 'retrieve':
            return [IsAuthenticated()]
        return [IsAdminOrReception()]

    def get_queryset(self):
        qs = super().get_queryset()
        venue_id = self.request.query_params.get('venue')
        if venue_id:
            qs = qs.filter(venue_id=venue_id)
        return qs

    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        slot = self.get_object()
        slot.is_active = not slot.is_active
        slot.save(update_fields=['is_active'])
        return Response({'code': 200, 'message': '状态已更新', 'data': {'is_active': slot.is_active}})

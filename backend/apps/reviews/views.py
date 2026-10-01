from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import Review, Favorite, Feedback
from .serializers import (
    ReviewSerializer, ReviewCreateSerializer, FavoriteSerializer, FeedbackSerializer,
)
from apps.users.permissions import IsAdminOrReception


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('user', 'booking__court__venue').all()

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'create'):
            return [IsAuthenticated()]
        return [IsAdminOrReception()]

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        venue = self.request.query_params.get('venue')
        if venue:
            try:
                qs = qs.filter(booking__court__venue_id=int(venue))
            except (TypeError, ValueError):
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'venue': 'venue 参数必须是数字'})
        return qs

    def perform_create(self, serializer):
        from apps.bookings.models import Booking
        booking = Booking.objects.select_related('user').get(pk=serializer.validated_data['booking'].pk)
        if booking.user_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('只能评价自己的订单')
        if booking.status != 'paid' or not booking.checked_in:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('仅已支付且已签到的订单可评价')
        try:
            # savepoint 隔离唯一约束冲突，避免污染外层测试事务
            with transaction.atomic():
                serializer.save(user=self.request.user)
        except IntegrityError:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('该订单已评价过')

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """商家回复（管理员/前台）"""
        review = self.get_object()
        reply = request.data.get('reply', '')
        if not reply.strip():
            return Response({'code': 400, 'message': '回复内容不能为空'}, status=400)
        review.reply = reply
        review.replied_at = timezone.now()
        review.save(update_fields=['reply', 'replied_at'])
        return Response({'code': 200, 'message': '已回复', 'data': ReviewSerializer(review).data})


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.select_related('venue').all()
    serializer_class = FavoriteSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        venue = serializer.validated_data['venue']
        try:
            with transaction.atomic():
                serializer.save(user=self.request.user)
        except IntegrityError:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('已收藏过该场馆')


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.select_related('user').all()
    serializer_class = FeedbackSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAdminOrReception()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == 'member':
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """标记已处理（管理员/前台）"""
        feedback = self.get_object()
        feedback.status = Feedback.STATUS_PROCESSED
        feedback.reply = request.data.get('reply', feedback.reply)
        feedback.processed_at = timezone.now()
        feedback.save(update_fields=['status', 'reply', 'processed_at'])
        return Response({'code': 200, 'message': '已处理', 'data': FeedbackSerializer(feedback).data})

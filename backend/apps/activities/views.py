from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import Activity, Registration
from .serializers import ActivitySerializer, RegistrationSerializer
from apps.users.permissions import IsAdminOrReception


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.select_related('venue').all()

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'register', 'cancel', 'my'):
            return [IsAuthenticated()]
        return [IsAdminOrReception()]

    serializer_class = ActivitySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        type_filter = self.request.query_params.get('type')
        if type_filter:
            qs = qs.filter(type=type_filter)
        is_active = self.request.query_params.get('is_active')
        if is_active in ('true', 'false'):
            qs = qs.filter(is_active=is_active == 'true')
        return qs

    @transaction.atomic
    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        """报名：行锁扣名额；取消后可重新报名"""
        if request.user.role != 'member':
            return Response({'code': 400, 'message': '仅会员可报名'}, status=400)
        activity = Activity.objects.select_for_update().get(pk=pk)
        now = timezone.now()
        if not activity.is_active:
            return Response({'code': 400, 'message': '活动未开放'}, status=400)
        if now > activity.deadline:
            return Response({'code': 400, 'message': '已过报名截止时间'}, status=400)

        reg = Registration.objects.filter(activity=activity, user=request.user).first()
        if reg is not None and reg.status == Registration.STATUS_REGISTERED:
            return Response({'code': 400, 'message': '你已报名该活动'}, status=400)
        if activity.registered >= activity.capacity:
            return Response({'code': 400, 'message': '名额已满'}, status=400)

        if reg is None:
            reg = Registration.objects.create(activity=activity, user=request.user, price=activity.price)
        else:
            reg.status = Registration.STATUS_REGISTERED
            reg.price = activity.price
            reg.save(update_fields=['status', 'price'])
        Activity.objects.filter(pk=activity.pk).update(registered=F('registered') + 1)
        return Response({'code': 200, 'message': '报名成功', 'data': RegistrationSerializer(reg).data})

    @transaction.atomic
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消报名，释放名额"""
        activity = Activity.objects.select_for_update().get(pk=pk)
        try:
            reg = Registration.objects.select_for_update().get(
                activity=activity, user=request.user,
            )
        except Registration.DoesNotExist:
            return Response({'code': 400, 'message': '未报名该活动'}, status=400)
        if reg.status == Registration.STATUS_REGISTERED:
            reg.status = Registration.STATUS_CANCELLED
            reg.save(update_fields=['status'])
            if activity.registered > 0:
                Activity.objects.filter(pk=activity.pk).update(registered=F('registered') - 1)
        return Response({'code': 200, 'message': '已取消报名'})

    @action(detail=False, methods=['get'])
    def my(self, request):
        qs = Registration.objects.filter(user=request.user).select_related('activity')
        return Response({'code': 200, 'data': RegistrationSerializer(qs, many=True).data})

    @action(detail=True, methods=['get'])
    def registrations(self, request, pk=None):
        """报名名单（管理员/前台）"""
        activity = self.get_object()
        qs = Registration.objects.filter(activity=activity).select_related('user')
        return Response({'code': 200, 'data': RegistrationSerializer(qs, many=True).data})

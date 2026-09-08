from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Announcement
from .serializers import AnnouncementSerializer
from apps.users.permissions import IsAdminOrReception


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

    def get_permissions(self):
        # 列表/详情对所有人开放（未登录也能看首页公告），管理操作仅管理员/前台
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAdminOrReception()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        # 非管理员/前台只看已发布的公告
        if not (user.is_authenticated and user.role in ('admin', 'reception')):
            qs = qs.filter(is_published=True)
        return qs

    @action(detail=True, methods=['post'])
    def toggle_publish(self, request, pk=None):
        obj = self.get_object()
        obj.is_published = not obj.is_published
        obj.save(update_fields=['is_published'])
        return Response({'code': 200, 'message': '状态已更新',
                         'data': {'is_published': obj.is_published}})

    @action(detail=True, methods=['post'])
    def toggle_pin(self, request, pk=None):
        obj = self.get_object()
        obj.is_pinned = not obj.is_pinned
        obj.save(update_fields=['is_pinned'])
        return Response({'code': 200, 'message': '状态已更新',
                         'data': {'is_pinned': obj.is_pinned}})

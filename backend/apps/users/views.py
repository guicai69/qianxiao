from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    RegisterSerializer, LoginSerializer, UserInfoSerializer,
    UserUpdateSerializer, ChangePasswordSerializer,
    AdminUserCreateSerializer, AdminUserUpdateSerializer,
)
from .permissions import IsAdmin, IsAdminOrReception, IsOwnerOrStaff


class RegisterView(generics.CreateAPIView):
    """用户注册"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'code': 200,
            'message': '注册成功',
            'data': {'id': user.id, 'phone': user.phone},
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """用户登录 — 返回 JWT token"""
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'code': 200,
            'message': '登录成功',
            'data': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserInfoSerializer(user).data,
            },
        })


class ChangePasswordView(generics.GenericAPIView):
    """修改密码"""
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'code': 200, 'message': '密码修改成功'})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')

    def get_queryset(self):
        qs = super().get_queryset()
        phone = self.request.query_params.get('phone')
        role = self.request.query_params.get('role')
        is_blacklisted = self.request.query_params.get('is_blacklisted')
        if phone:
            qs = qs.filter(phone__icontains=phone)
        if role:
            qs = qs.filter(role=role)
        if is_blacklisted not in (None, ''):
            qs = qs.filter(is_blacklisted=is_blacklisted.lower() in ('true', '1'))
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return AdminUserCreateSerializer
        if self.action in ('partial_update', 'update'):
            return AdminUserUpdateSerializer
        return UserInfoSerializer

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        if self.action in ('list', 'retrieve'):
            return [IsAdminOrReception()]
        if self.action in ('create', 'destroy'):
            return [IsAdmin()]
        return [IsAdminOrReception()]

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        """当前用户个人信息"""
        if request.method == 'PATCH':
            serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        serializer = UserInfoSerializer(request.user)
        return Response({'code': 200, 'data': serializer.data})

    def perform_destroy(self, instance):
        """硬删除用户"""
        instance.delete()

    @action(detail=True, methods=['post'])
    def blacklist(self, request, pk=None):
        user = self.get_object()
        user.is_blacklisted = True
        user.save(update_fields=['is_blacklisted'])
        return Response({'code': 200, 'message': '已拉黑'})

    @action(detail=True, methods=['post'])
    def unblacklist(self, request, pk=None):
        user = self.get_object()
        user.is_blacklisted = False
        user.save(update_fields=['is_blacklisted'])
        return Response({'code': 200, 'message': '已取消拉黑'})

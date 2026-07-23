from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CustomJWTAuthentication(JWTAuthentication):
    """扩展 JWT 认证 — 检查用户是否被禁用"""

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is not None:
            user, token = result
            if not user.is_active:
                raise AuthenticationFailed('该账号已被禁用')
        return result

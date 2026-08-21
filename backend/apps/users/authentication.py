from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is not None:
            user, token = result
            if not user.is_active:
                raise AuthenticationFailed('该账号已被禁用')
            if user.is_blacklisted:
                raise AuthenticationFailed('该账号已被拉黑')
        return result

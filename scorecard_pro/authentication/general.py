from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user: CustomUser):
    token = RefreshToken.for_user(user)
    token["full_name"] = user.full_name
    token["email"] = user.email
    token["mobile"] = user.mobile
    token['user_type'] = user.user_type
    # token['uuid'] = user.uuid
    # print('expiry time', token.access_token['exp'])
    return {
        'refresh': str(token),
        'access': str(token.access_token),
        'expiry_time': (token.access_token['exp'] * 1000)
    }
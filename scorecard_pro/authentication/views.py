from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from authentication.models import CustomUser
from authentication.serializers import CustomUserSerializer,UserLoginValidator,UserSignupValidator
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
        # 'refresh': str(token),
        'accessToken': str(token.access_token),
        'expiry_time': (token.access_token['exp'] * 1000)
    }

class SerializerError(Exception):
    
    def __init__(self, data):
        error_messages = []
        for field, error in data.items():
            error_message = str(error[0])
            error_messages.append(error_message)
        self.data = error_messages[0]
    
    def __str__(self):
        return self.data


class UserSignupView(APIView):
    def post(self, request):
        context = {
            'success':1,
            "message":'User created successfully',
            'data':[]
        }
        serializer = UserSignupValidator(data=request.data)
        if serializer.is_valid():
            user_data = serializer.validated_data
            user = CustomUser.objects.create(
                full_name=user_data['full_name'],
                mobile=user_data['mobile'],
                email=user_data['email'],
                user_type='super_admin'
            )
            user.set_password(user_data['password'])  # Hash the password
            user.save()

            return Response({**context, "user_id": user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.contrib.auth import authenticate,login

class UserLoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        context = {
            "success": 1,
            "message": "User logged in succesfully",
            "data": {}
        }
        try:
            validator = UserLoginValidator(data=request.data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)
            req_params = validator.validated_data
            auth_user = authenticate(request, email=req_params['email'], password=req_params['password'])
            print(auth_user)
            if auth_user is not None:
                login(request, auth_user)
                tokens = get_tokens_for_user(auth_user)
                context = { **tokens ,**context}
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)




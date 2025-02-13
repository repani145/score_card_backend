from django.urls import path
from . import views

urlpatterns = [
    path('create-user',views.UserSignupView.as_view(),name='create-user'),
    path('login',views.UserLoginView.as_view(),name='login'),
]
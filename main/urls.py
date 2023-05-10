from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from .swagger import schema_view
from . import views

urlpatterns = [
    path('redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('user', views.UserCreateView.as_view(), name='user_create'),
    path('token', views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh', views.TokenRefreshView.as_view(), name='token_refresh'),
    path('friendship', views.FriendshipCreateView.as_view(), name='friendship_create'),
    path('friendship/<int:user_id>', views.FriendshipDetailAPIView.as_view(), name='friendship_detail'),
    path('friendship/<int:user_id>/status', views.FriendshipStatusView.as_view(), name='friendship_status'),
    path('friendship/incoming', views.FriendshipRequestsView.as_view({'get': 'get_incoming_friendship_requests'}), name='incoming_friendship_requests'),
    path('friendship/outgoing', views.FriendshipRequestsView.as_view({'get': 'get_outgoing_friendship_requests'}), name='outgoing_friendship_requests'),
    path('friendship/friends', views.FriendshipRequestsView.as_view({'get': 'get_friends'})),
]

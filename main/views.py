from django.db import transaction
from django.db.models import Q
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Friendship, User
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics, status
from .serializers import UserSerializer, MyTokenObtainPairSerializer, FriendshipSerializer, \
    IncomingFriendshipSerializer, OutgoingFriendshipSerializer, FriendSerializer, StatusSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from . import errors


class TokenRefreshView(TokenRefreshView):
    pass


class UserCreateView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    authentication_classes = []

    @swagger_auto_schema(
        operation_id='create_user',
        responses={201: "", 400: errors.HTTP_400},
    )
    def post(self, request, *args, **kwargs):
        """Ничего не стоит возвращать"""
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return User.objects.all()


class TokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def get_queryset(self):
        return Friendship.objects.all()


class FriendshipCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{"Bearer": []}],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['to_user'],
            properties={
                'to_user': openapi.Schema(type=openapi.TYPE_STRING, description='username')
            }
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description='Заявка дружбы успешно отправлена.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Ошибка валидации запроса дружбы.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def post(self, request, format=None):
        serializer = FriendshipSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            response_data = serializer.create(serializer.validated_data)
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return Friendship.objects.all()


class FriendshipDetailAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{"Bearer": []}],
        operation_id='update_friendship',
        responses={200: "", 400: errors.HTTP_400, 401: "", 404: None},
    )
    @transaction.atomic
    def put(self, request, user_id, format=None):
        user = User.objects.get(id=request.user.id)
        try:
            friendship = Friendship.objects.select_for_update().get(to_user__id=user_id, from_user=user,
                                                                    status=Friendship.PENDING)
        except Friendship.DoesNotExist:
            return Response({'error': 'Friendship request not found.'}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        if action == 'accept':
            friendship.status = Friendship.ACCEPTED
            friendship.save()

        elif action == 'reject':
            friendship.status = Friendship.REJECTED
            friendship.save()

        else:
            return Response({'error': 'Action not recognized.'}, status=status.HTTP_400_BAD_REQUEST)

        if friendship.status == Friendship.ACCEPTED:
            friendship.status = Friendship.FRIENDS
            friendship.save()
            Friendship.objects.create(from_user=friendship.to_user, to_user=friendship.from_user,
                                      status=Friendship.FRIENDS)

        return Response(status.HTTP_200_OK)

    @swagger_auto_schema(
        security=[{"Bearer": []}],
        operation_id='delete_friendship',
        responses={204: "", 400: errors.HTTP_400, 401: "", 404: None},
    )
    def delete(self, request, user_id):
        user = User.objects.get(id=request.user.id)
        try:
            friend = Friendship.objects.get(
                from_user=user,
                to_user__id=user_id,
                status=Friendship.FRIENDS
            )
        except Friendship.DoesNotExist:
            return Response(
                {'error': 'Friendship does not exist.'},
                status=status.HTTP_404_NOT_FOUND
            )
        friend.delete_friendship()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        return Friendship.objects.all()


class FriendshipStatusView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{"Bearer": []}],
        operation_id='get_friendship_status',
        responses={200: StatusSerializer, 400: errors.HTTP_400, 401: "", 404: None},
    )
    def get(self, request, user_id, format=None):
        user = User.objects.get(id=request.user.id)

        try:
            friend = User.objects.get(id=user_id)
            outgoing_request = Friendship.objects.filter(from_user=user, to_user=friend, status='pending').exists()
            incoming_request = Friendship.objects.filter(from_user=friend, to_user=user, status='pending').exists()
            if user == friend:
                status = 'self'
            elif outgoing_request:
                status = 'outgoing_request'
            elif incoming_request:
                status = 'incoming_request'
            elif user.friends.filter(id=friend.id).exists():
                status = 'friends'
            else:
                status = 'not_friends'
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'status': status})

    def get_queryset(self):
        return Friendship.objects.all()


class FriendshipRequestsView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{"Bearer": []}],
        operation_id='get_friends',
        responses={200: FriendSerializer(many=True), 400: errors.HTTP_400, 401: ""},
    )
    def get_friends(self, request):
        user = User.objects.get(id=request.user.id)
        friends = Friendship.objects.filter(
            Q(from_user=user, status=Friendship.FRIENDS) & Q(to_user=user, status=Friendship.FRIENDS)
        )
        friend_users = set(friend.from_user.user.username if friend.to_user == user else friend.to_user.user.username for friend in friends)
        return Response({'friends': friend_users}, status.HTTP_200_OK)

    @swagger_auto_schema(
        security=[{"Bearer": []}],
        operation_id='get_incoming_friendship_requests',
        responses={200: IncomingFriendshipSerializer, 400: errors.HTTP_400, 401: ""},
    )
    def get_incoming_friendship_requests(self, request):
        user = User.objects.get(id=request.user.id)
        incoming_requests = Friendship.objects.filter(to_user=user, status='pending')
        serializer = IncomingFriendshipSerializer(incoming_requests, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        security=[{"Bearer": []}],
        operation_id='get_outgoing_friendship_requests',
        responses={status.HTTP_200_OK: OutgoingFriendshipSerializer(many=True), 400: errors.HTTP_400, 401: ""},
    )
    def get_outgoing_friendship_requests(self, request):
        user = User.objects.get(id=request.user.id)
        outgoing_requests = Friendship.objects.filter(from_user=user, status='pending')
        serializer = OutgoingFriendshipSerializer(outgoing_requests, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        return Friendship.objects.all()

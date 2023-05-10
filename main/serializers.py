from requests import Response
from .models import User
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers, status
from .models import Friendship
from django.contrib.auth.models import User as AuthUser


class FriendshipSerializer(serializers.Serializer):
    to_user = serializers.CharField(max_length=150)

    def create(self, validated_data):
        user = User.objects.get(user__id=self.context['request'].user.id)
        friend_username = validated_data.get('to_user')
        try:
            friend = User.objects.get(user__username=friend_username)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": f'Пользователь "{friend_username}" не найден'})

        if user == friend:
            raise serializers.ValidationError({"error": 'Вы не можете отправить запрос на дружбу самому себе.'})

        # Проверяем, есть ли уже активная заявка между пользователями
        existing_friendship = Friendship.objects.filter(
            from_user=user,
            to_user=friend,
            status__in=[Friendship.PENDING, Friendship.ACCEPTED, Friendship.FRIENDS, Friendship.DELETED]
        ).first()

        check = Friendship.objects.filter(
            from_user=friend,
            to_user=user,
            status__in=[Friendship.PENDING, Friendship.DELETED, Friendship.REJECTED]).first()

        if existing_friendship:
            if existing_friendship.status == Friendship.ACCEPTED:
                raise serializers.ValidationError({"error": 'Вы уже друзья с этим пользователем.'})
            elif existing_friendship.status == Friendship.PENDING:
                raise serializers.ValidationError({"error": 'Запрос на дружбу уже отправлен.'})
            elif existing_friendship.status == Friendship.DELETED:
                raise serializers.ValidationError({"error": 'Пользователь удален из друзей'})
            elif check and check.status in [Friendship.DELETED, Friendship.REJECTED]:
                raise serializers.ValidationError({"error": 'Пользователь отклонил ваш запрос или удалил из друзей'})
            else:
                # existing_friendship.status == Friendship.FRIENDS
                raise serializers.ValidationError({"error": 'Вы уже друзья с этим пользователем.'})
        else:
            # Создаем новую заявку на дружбу
            if not check:
                friendship_request = Friendship(from_user=user, to_user=friend, status=Friendship.PENDING)
                friendship_request.save()
                return {'success': 'Запрос на дружбу отправлен успешно.'}

            friendship_request = Friendship(from_user=user, to_user=friend, status=Friendship.FRIENDS)
            friendship_request.save()
            check.status = Friendship.FRIENDS
            check.save()
            return {'success': f'{friend.user.username} добавлен в друзья'}


class IncomingFriendshipSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(source='from_user.id')
    username = serializers.CharField(source='from_user.user.username', max_length=150)
    created_at = serializers.DateTimeField()


class OutgoingFriendshipSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(source='to_user.id')
    username = serializers.CharField(source='to_user.user.username', max_length=150)
    created_at = serializers.DateTimeField()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Добавить дополнительные поля в токен, если необходимо
        token['username'] = user.username
        return token


class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        password = validated_data.pop('password')
        username = validated_data.get('username')
        if AuthUser.objects.filter(username=username).exists():
            raise ValidationError({"error": "This username is already taken."}, code='invalid')
        auth_user = AuthUser.objects.create_user(**validated_data, password=password)
        user = User.objects.create(user=auth_user)
        return user

    def to_representation(self, instance):
        # Отображение объекта юзера
        return {}

    class Meta:
        model = User
        fields = ['__all__']


class FriendSerializer(serializers.Serializer):
    username = serializers.CharField()



class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ['status']

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import User as MyUser, Friendship
from django.contrib.auth.models import User


class TokenRefreshViewTestCase(APITestCase):
    def test_token_refresh_view(self):
        client = APIClient()
        url = reverse('token_refresh')
        response = client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserCreateViewTestCase(APITestCase):
    def test_user_create_view(self):
        client = APIClient()
        url = reverse('user_create')
        data = {
            'username': 'test_user',
            'password': 'test_password'
        }
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TokenObtainPairViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')

    def test_token_obtain_pair_view(self):
        client = APIClient()
        url = reverse('token_obtain_pair')
        data = {
            'username': 'test_user',
            'password': 'test_password'
        }
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class FriendshipCreateViewTestCase(APITestCase):
    def setUp(self):
        self.user1 = MyUser.objects.create(
            user=User.objects.create_user(username='test_user1', password='test_password'))
        self.user2 = MyUser.objects.create(
            user=User.objects.create_user(username='test_user2', password='test_password'))

    def test_friendship_create_view(self):
        client = APIClient()
        client.force_authenticate(user=self.user1.user)
        url = reverse('friendship_create')
        data = {
            'to_user': self.user2.user.username
        }
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class FriendshipDetailAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user1 = MyUser.objects.create(
            user=User.objects.create_user(username='test_user1', password='test_password'))
        self.user2 = MyUser.objects.create(
            user=User.objects.create_user(username='test_user2', password='test_password'))
        self.friendship = Friendship.objects.create(from_user=self.user1, to_user=self.user2, status=Friendship.PENDING)

    def test_friendship_detail_api_view(self):
        client = APIClient()
        client.force_authenticate(user=self.user1.user)
        url = reverse('friendship_detail', kwargs={'user_id': self.user2.id})
        data = {
            'action': 'accept'
        }
        response = client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class FriendshipStatusViewTestCase(APITestCase):
    def setUp(self):
        self.user1 = MyUser.objects.create(
            user=User.objects.create_user(username='test_user1', password='test_password'))
        self.user2 = MyUser.objects.create(
            user=User.objects.create_user(username='test_user2', password='test_password'))
        self.friendship = Friendship.objects.create(from_user=self.user1, to_user=self.user2, status=Friendship.PENDING)

    def test_friendship_status_view(self):
        client = APIClient()
        client.force_authenticate(user=self.user1.user)
        url = reverse('friendship_status', kwargs={'user_id': self.user2.user.id})
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class FriendshipRequestsViewTestCase(APITestCase):
    def setUp(self):
        self.user1 = MyUser.objects.create(
            user=User.objects.create_user(username='test_user1', password='test_password'))
        self.user2 = MyUser.objects.create(
            user=User.objects.create_user(username='test_user2', password='test_password'))
        self.client.force_authenticate(user=self.user1.user)

    def test_create_friendship_request(self):
        url = reverse('friendship_create')
        data = {'to_user': self.user2.user.username}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_friendship_requests_incoming(self):
        url = reverse('incoming_friendship_requests')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_friendship_requests_outgoing(self):
        url = reverse('outgoing_friendship_requests')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_accept_friendship_request(self):
    #     url = reverse('friendship-requests')
    #     data = {'to_user': self.user2.id}
    #     self.client.post(url, data, format='json')
    #     friendship_request_id = self.user2.friendship_requests_received.first().id
    #     url = reverse('friendship-request-action', kwargs={'pk': friendship_request_id})
    #     data = {'action': 'accept'}
    #     response = self.client.patch(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    # def test_reject_friendship_request(self):
    #     url = reverse('friendship-requests')
    #     data = {'to_user': self.user2.id}
    #     self.client.post(url, data, format='json')
    #     friendship_request_id = self.user2.friendship_requests_received.first().id
    #     url = reverse('friendship-request-action', kwargs={'pk': friendship_request_id})
    #     data = {'action': 'reject'}
    #     response = self.client.patch(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
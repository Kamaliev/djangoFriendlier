from django.db import models


class User(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='main_user')
    friends = models.ManyToManyField('self', through='Friendship', symmetrical=False,
                                     related_name='friendship_users')

    def __str__(self):
        return f"{self.user.username}"


class Friendship(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    DELETED = 'deleted'
    FRIENDS = 'friends'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (DELETED, 'Deleted'),
        (FRIENDS, 'Friends')
    ]

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friendship_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendship_requests_received')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def delete_friendship(self):
        self.status = self.DELETED
        self.save()

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(null=True, blank=True, upload_to='accounts/profiles/avatar')

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('accounts:profile')

    @property
    def avatar_url(self):
        return self.avatar.url if self.avatar else f'{settings.STATIC_URL}images/users/profile.svg'

    # найти профиль пользователя по e-mail
    @staticmethod
    def get_by_email(email):
        return Profile.objects.filter(email__exact=email).first()




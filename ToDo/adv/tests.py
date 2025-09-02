from django.test import TestCase

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ToDo.settings")

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from .models import Advertisement, FavoriteAdvertisement, \
    AdvertisementStatusChoices

User = get_user_model()


class AdvertisementTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='pass')
        self.admin = User.objects.create_user(username='admin', password='pass')

        self.adv1 = Advertisement.objects.create(
            title='тестовое тесто',
            description='описание',
            status=AdvertisementStatusChoices.OPEN,
            creator=self.user
        )
        self.ad2 = Advertisement.objects.create(
            title="Черновичек",
            description="Черновик",
            status=AdvertisementStatusChoices.DRAFT,
            creator=self.user
        )
        self.client_user = APIClient()
        self.client_user.login(username='user1', password='pass')

        self.client_user = APIClient()
        self.client_user.login(username='admin', password='pass')

    def test_delete_other_advertisement_forbidden(self):
        other_user = User.objects.create_user(username="user2", password="pass")
        ad = Advertisement.objects.create(title="Другое", status="OPEN",
                                          creator=other_user)
        response = self.client_user.delete(f"/ads/{ad.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_any_advertisement(self):
        ad = Advertisement.objects.create(title="Другое", status="OPEN",
                                          creator=self.user)
        response = self.client_admin.delete(f"/ads/{ad.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

from django.test import TestCase, Client
from django.core.cache import cache

from posts.models import User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')

    def setUp(self):
        cache.clear()

        self.user = User.objects.get(username='test-user')

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_not_exsist_page(self):
        response = self.authorized_client.get('/magic_page/')
        self.assertEqual(response.status_code, 404)

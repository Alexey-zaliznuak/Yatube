from django.test import Client, TestCase
from django.urls import reverse

from ..views import POSTS_PER_PAGE
from ..models import Post, Group, User
from .test_urls import INDEX_URL, PROFILE_URL


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-desc',
        )

        new_posts = [
            Post(
                author=cls.user,
                text=f'test-post{i}',
                group=cls.group
            ) for i in range(1, 14)
        ]

        Post.objects.bulk_create(new_posts)

    def setUp(self):
        self.user = User.objects.get(username='test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse(INDEX_URL))
        # Проверка: количество постов на первой странице равно POSTS_PER_PAGE.
        self.assertEqual(len(response.context['page_obj']), POSTS_PER_PAGE)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse(INDEX_URL) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_person_page_contains_ten_records(self):
        response = self.client.get(
            reverse(PROFILE_URL, kwargs={'username': 'test-user'})
        )
        # Проверка: количество постов на первой странице равно POSTS_PER_PAGE.
        self.assertEqual(len(response.context['page_obj']), POSTS_PER_PAGE)

from django.test import TestCase, Client
from django.core.cache import cache
from django.urls import reverse

from ..models import Post, Group, User


INDEX_URL = 'posts:index'
FOLLOW_INDEX_URL = 'posts:follow_index'

GROUP_LIST_URL = 'posts:group_list'

FOLLOW_URL = 'posts:profile_follow'
UNFOLLOW_URL = 'posts:profile_unfollow'

CREATE_POST_URL = 'posts:post_create'
EDIT_POST_URL = 'posts:post_edit'
POST_DETAIL_URL = 'posts:post_detail'

CREATE_COMMENT_URL = 'posts:add_comment'

PROFILE_URL = 'posts:profile'


CREATE_POST_TEMPLATE = 'posts/create_post.html'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

        self.user = User.objects.create_user(username='HasNoName')

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.post_author_user = User.objects.get(username='auth')

        self.post_author_user_client = Client()
        self.post_author_user_client.force_login(self.post_author_user)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test/',
            'posts/profile.html': '/profile/HasNoName/',
            'posts/post_detail.html': '/posts/1/',

        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_edit_post_edit_permission(self):
        url = '/posts/1/edit/'
        response = self.authorized_client.get(url, follow=True)
        self.assertRedirects(
            response, '/posts/1/'
        )

        response = self.post_author_user_client.get(url)
        self.assertTemplateUsed(response, CREATE_POST_TEMPLATE)

    def test_create_post_permission(self):
        response = self.authorized_client.get(reverse(CREATE_POST_URL))
        self.assertTemplateUsed(response, CREATE_POST_TEMPLATE)

        response = self.guest_client.get(reverse(CREATE_POST_URL))
        self.assertRedirects(response, '/auth/login/?next=/create/')


class FollowTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-follower-user')
        cls.author = User.objects.create_user(username='test-author-user')

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

        self.user = User.objects.get(username='test-follower-user')
        self.author = User.objects.get(username='test-author-user')

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_permission_follow(self):
        response = self.guest_client.get(reverse(
            FOLLOW_URL, kwargs={'username': 'test-author-user'}
        ),
            follow=True
        )
        self.assertRedirects(
            response, '/auth/login/?next=/profile/test-author-user/follow/'
        )

    def test_auth_permission_follow(self):
        response = self.authorized_client.get(reverse(
            FOLLOW_URL, kwargs={'username': 'test-author-user'}
        ),
            follow=True
        )
        self.assertRedirects(response, reverse(
            PROFILE_URL, kwargs={'username': 'test-author-user'}
        ))

    def test_guest_permission_unfollow(self):
        response = self.guest_client.get(reverse(
            UNFOLLOW_URL, kwargs={'username': 'test-author-user'}
        ),
            follow=True
        )
        self.assertRedirects(
            response, '/auth/login/?next=/profile/test-author-user/unfollow/'
        )

    def test_auth_permission_unfollow(self):
        response = self.authorized_client.get(reverse(
            UNFOLLOW_URL, kwargs={'username': 'test-author-user'}
        ),
            follow=True
        )
        self.assertRedirects(response, reverse(
            PROFILE_URL, kwargs={'username': 'test-author-user'}
        ))

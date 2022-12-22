
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, User, Group, Comment
from .test_urls import (
    EDIT_POST_URL,
    CREATE_POST_URL,
    CREATE_COMMENT_URL,
)


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test-author-user')
        cls.group = Group.objects.create(
            title="test-title",
            slug="test-slug",
            description="test-descrition",
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='test-post',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create_user(username='test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.author = User.objects.get(username="test-author-user")
        self.author_client = Client()
        self.author_client.force_login(self.author)

        self.edit_form_data = {'text': 'test-edit-text'}
        self.edit_kwargs = {
            'path': reverse(EDIT_POST_URL, kwargs={'post_id': 1}),
            'data': self.edit_form_data,
            'follow': True,
        }
        self.create_kwargs = {
            'path': reverse(CREATE_POST_URL),
            'data': {'text': 'test-new-text'},
            'follow': True,
        }

    def test_guest_cant_create_post(self):
        Posts_count = Post.objects.count()
        gues_resp = self.guest_client.post(**self.create_kwargs)
        self.assertEqual(Post.objects.count(), Posts_count)

        self.assertEqual(gues_resp.status_code, 200)

    def test_auth_can_create_post(self):
        Posts_count = Post.objects.count()
        auth_resp = self.authorized_client.post(**self.create_kwargs)
        self.assertEqual(Post.objects.count(), Posts_count + 1)

        self.assertEqual(auth_resp.status_code, 200)

    def test_guest_cant_edit_post(self):
        resp = self.guest_client.post(**self.edit_kwargs)
        self.assertNotEqual(
            Post.objects.get(pk=1).text, self.edit_form_data['text']
        )
        self.assertEqual(resp.status_code, 200)

    def test_auth_user_cant_edit_post(self):
        resp = self.authorized_client.post(**self.edit_kwargs)
        self.assertNotEqual(
            Post.objects.get(pk=1).text, self.edit_form_data['text']
        )
        self.assertEqual(resp.status_code, 200)

    def test_author_can_edit_post(self):
        resp = self.author_client.post(**self.edit_kwargs)
        self.assertEqual(
            Post.objects.get(pk=1).text, self.edit_form_data['text']
        )
        self.assertEqual(resp.status_code, 200)


class CommentCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test-user')
        cls.post = Post.objects.create(
            author=cls.author,
            text='test-post',
        )

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.get(username='test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.kwargs = {
            'path': reverse(CREATE_COMMENT_URL, kwargs={'post_id': 1}),
            'data': {'text': 'test-new-comment-text'},
            'follow': True,
        }

    def test_guest_cant_create_comment(self):
        Comments_count = Comment.objects.count()
        gues_resp = self.guest_client.post(**self.kwargs)
        self.assertEqual(Comments_count, Comment.objects.count())
        self.assertEqual(gues_resp.status_code, 200)

    def test_auth_can_create_comment(self):
        Comments_count = Comment.objects.count()
        auth_resp = self.authorized_client.post(**self.kwargs)
        self.assertEqual(Comment.objects.count(), Comments_count + 1)
        self.assertEqual(auth_resp.status_code, 200)

import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from time import sleep

from ..models import Post, Group, User, Comment, Follow
from ..forms import PostForm

from .test_urls import (
    FOLLOW_INDEX_URL,
    CREATE_POST_URL,
    POST_DETAIL_URL,
    GROUP_LIST_URL,
    EDIT_POST_URL,
    UNFOLLOW_URL,
    PROFILE_URL,
    FOLLOW_URL,
    INDEX_URL,
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-describe',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test-post',
        )

    def setUp(self):
        cache.clear()
        self.user = User.objects.get(username='test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse(
                POST_DETAIL_URL, kwargs={'post_id': 1}
            ): 'posts/post_detail.html',
            reverse(
                EDIT_POST_URL, kwargs={'post_id': Post.objects.first().id}
            ): 'posts/create_post.html',
            reverse(CREATE_POST_URL): 'posts/create_post.html',
            reverse(INDEX_URL): 'posts/index.html',
            reverse(
                GROUP_LIST_URL, kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                PROFILE_URL, kwargs={'username': 'test-user'}
            ): 'posts/profile.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class groupPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-desc',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='test-post1',
            group=cls.group,
        )

        sleep(0.1)

        cls.post = Post.objects.create(
            author=cls.user,
            text='test-post2',
            group=cls.group,
        )

    def setUp(self):
        cache.clear()
        self.user = User.objects.get(username='test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_show_correct_context(self):
        response = self.authorized_client.get(reverse(INDEX_URL))
        self.assertIsNotNone(response.context['page_obj'])

    def test_post_detail(self):
        response = (self.authorized_client.get(
            reverse(POST_DETAIL_URL, kwargs={'post_id': 1}))
        )
        self.assertEqual(response.context.get('post').text, 'test-post1')
        self.assertEqual(response.context.get('post').id, 1)
        self.assertEqual(response.context.get('post').author, self.user)

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(GROUP_LIST_URL, kwargs={'slug': 'test-slug'})
        )

        first_object = response.context['page_obj'][0]
        self.assertEqual(response.context['group'], self.group)

        self.assertEqual(first_object.text, 'test-post2')

        for post in response.context['page_obj']:
            self.assertEqual(post.group, self.group)

    def test_profile(self):
        response = self.authorized_client.get(
            reverse(
                PROFILE_URL, kwargs={'username': 'test-user'}
            )
        )
        self.assertEqual(response.context['author'], self.user)

        for post in response.context['page_obj']:
            self.assertEqual(post.author, self.user)

    def test_create_form_correct_context(self):
        response = self.authorized_client.get(reverse(CREATE_POST_URL))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_form_correct_context(self):
        response = self.authorized_client.get(
            reverse(EDIT_POST_URL, kwargs={'post_id': 1})
        )

        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PostsInPageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-desc',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='test-post1',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='test-post2',
            group=cls.group,
        )

    def setUp(self):
        cache.clear()
        self.user = User.objects.get(username='test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_in_pages(self):
        rev_list = [
            reverse(GROUP_LIST_URL, kwargs={'slug': 'test-slug'}),
            reverse(INDEX_URL),
            reverse(PROFILE_URL, kwargs={'username': 'test-user'}),
        ]

        for index, rev in enumerate(rev_list):
            expect_len = 2
            if rev == reverse(
                GROUP_LIST_URL, kwargs={'slug': 'test-slug'}
            ):
                expect_len = 1

            response = self.authorized_client.get(rev)
            self.assertEqual(len(response.context["page_obj"]), expect_len)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateImageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.form = PostForm()
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-describe',
        )
        uploaded = SimpleUploadedFile(
            name='test.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )

        Post.objects.create(
            text='test-post-with-img',
            author=cls.user,
            image=uploaded,
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()

        self.user = User.objects.get(username='test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        post_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'test-image-text',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse(CREATE_POST_URL),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            PROFILE_URL, kwargs={'username': 'test-user'}
        ))

        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='test-image-text',
                image='posts/small.gif',
            ).exists()
        )

    def test_exist_image_in_context(self):
        pages_names = [
            reverse(GROUP_LIST_URL, kwargs={'slug': 'test-slug'}),
            reverse(PROFILE_URL, kwargs={'username': 'test-user'}),
        ]

        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse_name):
                resp = self.authorized_client.get(reverse_name)
                post = resp.context.get('page_obj')[0]
                self.assertIsNotNone(post.image)

    def test_exist_image_in_pages_with_one_post_context(self):
        pages = [
            reverse(INDEX_URL),
            reverse(POST_DETAIL_URL, kwargs={'post_id': 1})
        ]
        for reverse_name in pages:
            with self.subTest(reverse_name=reverse_name):
                resp = self.authorized_client.get(reverse_name)
                post = resp.context.get('post')
                self.assertIsNotNone(post.image)


class CommentInContextTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        post = Post.objects.create(
            text='test-post-with-img',
            author=cls.user,
        )
        Comment.objects.create(
            text='test-comment-text',
            post=post,
            author=cls.user
        )

    def setUp(self):
        self.user = User.objects.get(username='test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_exist_comment_in_post_detail_context(self):
        resp = self.authorized_client.get(reverse(
            POST_DETAIL_URL, kwargs={'post_id': 1}
        ))

        comments = resp.context.get('comments')
        self.assertIsNotNone(comments)


class CachePageTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.post = Post.objects.create(
            text="test-post-text",
            author=cls.user
        )

    def setUp(self):
        self.user = User.objects.get(username='test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache(self):
        cache.clear()
        self.authorized_client.get(reverse(INDEX_URL))

        Post.objects.create(
            text="test-post-text",
            author=self.user
        )

        new_resp = self.authorized_client.get(reverse(INDEX_URL))
        context = new_resp.context
        self.assertIsNone(context)

        cache.clear()

        new_resp = self.authorized_client.get(reverse(INDEX_URL))
        context = new_resp.context
        self.assertIsNotNone(context)


class FollowInContextTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='test-user-follower')
        cls.author = User.objects.create_user(username='test-user-author1')
        cls.second_user = User.objects.create_user(username='test-second-user')

        new_posts = [
            Post(
                author=cls.author,
                text=f'test-post{i}',
            ) for i in range(1, 4)
        ]

        Post.objects.bulk_create(new_posts)
        Follow.objects.create(
            user=cls.user,
            author=cls.author,
        )

    def setUp(self):
        cache.clear()
        self.user = User.objects.get(username='test-user-follower')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.second_user = User.objects.get(username='test-second-user')
        self.second_authorized_client = Client()
        self.second_authorized_client.force_login(self.second_user)

    def test_follows_in_context(self):
        resp = self.authorized_client.get(
            reverse(FOLLOW_INDEX_URL)
        )
        posts = resp.context.get('page_obj')
        self.assertEqual(len(posts), 3)

    def test_follows_post_not_exist_in_follower_context(self):
        resp = self.second_authorized_client.get(
            reverse(FOLLOW_INDEX_URL)
        )
        posts = resp.context.get('page_obj')
        self.assertEqual(len(posts), 0)

    def test_follows_created(self):
        Follows_count = Follow.objects.count()
        self.second_authorized_client.get(reverse(
            FOLLOW_URL, kwargs={'username': 'test-user-author1'}
        ))

        self.assertEqual(Follow.objects.count(), Follows_count + 1)

    def test_follows_deleted(self):
        Follows_count = Follow.objects.count()
        self.authorized_client.get(reverse(
            UNFOLLOW_URL, kwargs={'username': 'test-user-author1'}
        ))
        self.assertEqual(Follow.objects.count(), Follows_count - 1)

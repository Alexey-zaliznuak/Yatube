from django.test import TestCase

from ..models import Group, Post, User

LEN_POST_SHORT_DESCRIBE = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        post = PostModelTest.post
        expected_object_name = post.text[:LEN_POST_SHORT_DESCRIBE]
        self.assertEqual(
            expected_object_name, str(post)[:LEN_POST_SHORT_DESCRIBE]
        )

        group = PostModelTest.group
        expected_object_name = self.group.title
        self.assertEqual(expected_object_name, str(group))

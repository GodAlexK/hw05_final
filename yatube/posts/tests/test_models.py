from django.test import TestCase

from posts.models import Group, Post, User, Comment


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
            text='Длина этого текста должна быть не больше пятнадцати знаков',
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='Текст комментария',
        )

    def test_models_have_correct_object_post_text_and_title(self):
        correct_object_names = (
            (str(self.post), self.post.text[:15]),
            (str(self.group), self.group.title),
            (str(self.comment), self.comment.text),
        )
        for value, expected in correct_object_names:
            with self.subTest(value=value):
                self.assertEqual(value, expected)

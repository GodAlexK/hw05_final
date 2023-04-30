import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from http import HTTPStatus

from posts.models import Group, Post, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

INDEX_URL = reverse('posts:index')
GROUP_LIST_URL = reverse('posts:group_list', kwargs={'slug': 'test-slug'})
PROFILE_URL = reverse('posts:profile', kwargs={'username': 'test-user'})
POST_CREATE_URL = reverse('posts:post_create')
IMAGE_WAY = 'posts/small.gif'
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test-user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.comment = Post.objects.create(
            author=cls.user,
            text='Тестовый комментария',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.post_detail_url = reverse('posts:post_detail',
                                      kwargs={'post_id':
                                              cls.post.id}
                                      )
        cls.post_edit_url = reverse('posts:post_edit',
                                    kwargs={'post_id':
                                            cls.post.id}
                                    )
        cls.comment_url = reverse('posts:add_comment',
                                  kwargs={'post_id':
                                          cls.post.id}
                                  )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create_form(self):
        """"Создание записи в базе данных при отправке валидной формы."""
        post_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(POST_CREATE_URL,
                                               data=form_data,
                                               follow=True
                                               )
        self.assertRedirects(response, PROFILE_URL)
        self.assertEqual(Post.objects.count(), post_count + 1)
        post_latest = Post.objects.last()
        self.assertEqual(post_latest.text, form_data['text'])
        self.assertEqual(post_latest.group.id, form_data['group'])
        self.assertEqual(post_latest.image.name, IMAGE_WAY)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_form(self):
        """"Изменение поста в базе данных при отправке валидной формы."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Изменение текста поста',
            'group': self.group.id,
        }
        response = self.authorized_client.post(self.post_edit_url,
                                               data=form_data,
                                               follow=True
                                               )
        self.assertRedirects(response, self.post_detail_url)
        self.assertEqual(Post.objects.count(), post_count)
        post = Post.objects.get(pk=self.post.id)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])

    def test_not_post_create_form_anonymous(self):
        """"Неавторизованный пользователь не может создать запись."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        response = self.guest_client.post(POST_CREATE_URL,
                                          data=form_data,
                                          follow=True
                                          )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(Post.objects.count(), post_count + 1)

    def test_authorized_user_not_edit_another_post(self):
        """"Авторизованный пользователь не может отредактировать чужой пост."""
        self.authorized_client.login(username='2')
        post_count = Post.objects.count()
        form_data = {
            'text': 'Изменение текста поста',
            'group': self.group.id,
        }
        response = self.authorized_client.post(self.post_edit_url,
                                               data=form_data,
                                               follow=True
                                               )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), post_count)

    def test_not_send_comment_anonymous(self):
        """Проверка, что комментировать посты
        может только авторизованный пользователь."""
        self.guest_client.post(self.comment_url,
                               data={'text': 'Тестовый комментарий'},
                               follow=True
                               )
        self.assertIsNone(Comment.objects.first())

    def test_not_send_comment_anonymous(self):
        """Проверка, что после комментарий виден на
        странице поста после отправки."""
        form_data = {
            'text': 'Тестовый комментарий'
        }
        response = self.authorized_client.post(self.comment_url,
                                               data=form_data,
                                               follow=True
                                               )
        comment = Comment.objects.first()
        self.assertEqual(comment.text, form_data['text'])
        self.assertRedirects(response, self.post_detail_url)

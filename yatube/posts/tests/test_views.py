import shutil
import tempfile

from http import HTTPStatus

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from posts.models import Group, Post, Follow, User, POSTS_ON_THE_PAGE

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

POSTS_ON_THE_SECOND_PAGE = 3

INDEX_URL = reverse('posts:index')
GROUP_LIST_URL = reverse('posts:group_list', kwargs={'slug': 'test-slug'})
PROFILE_URL = reverse('posts:profile', kwargs={'username': 'test-user'})
POST_CREATE_URL = reverse('posts:post_create')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test-user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            image=uploaded,
        )
        POST_DETAIL_URL = reverse('posts:post_detail',
                                  kwargs={'post_id': cls.post.id}
                                  )
        POST_EDIT_URL = reverse('posts:post_edit',
                                kwargs={'post_id': cls.post.id}
                                )
        COMMENT_URL = reverse('posts:add_comment',
                              kwargs={'post_id': cls.post.id})
        cls.templates_pages_names = {
            INDEX_URL: 'posts/index.html',
            GROUP_LIST_URL: 'posts/group_list.html',
            PROFILE_URL: 'posts/profile.html',
            POST_DETAIL_URL: 'posts/post_detail.html',
            POST_EDIT_URL: 'posts/create_post.html',
            POST_CREATE_URL: 'posts/create_post.html',
            COMMENT_URL: 'posts:add_comment',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_views_uses_correct_template(self):
        """URL - адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Список постов в шаблоне index
        сформирован с правильным контекстом."""
        response = self.guest_client.get(INDEX_URL)
        post_one = response.context['page_obj'][0]
        post_author_0 = post_one.author
        post_text_0 = post_one.text
        post_image_0 = post_one.image
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_text_0, 'Тестовый пост')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_group_list_show_correct_context(self):
        """Список постов в шаблоне group_list
        сформирован с правильным контекстом, отфильтрованных по группе."""
        response = self.guest_client.get(GROUP_LIST_URL)
        group_one = response.context['group']
        group_title = group_one.title
        group_slug = group_one.slug
        group_description = group_one.description
        self.assertEqual(group_title, 'Тестовая группа')
        self.assertEqual(group_slug, 'test-slug')
        self.assertEqual(group_description, 'Тестовое описание')

    def test_profile_show_correct_context(self):
        """Список постов в шаблоне profile сформирован
        с правильным контекстом, отфильтрованных по пользователю."""
        response = self.guest_client.get(PROFILE_URL)
        post_author = response.context['page_obj'][0]
        profile_author = post_author.author
        self.assertEqual(profile_author, self.user)

    def test_post_detail_show_correct_context(self):
        """Пост в шаблоне post_detail сформирован
        с правильным контекстом, отфильтрованный по id."""
        POST_DETAIL_URL = reverse('posts:post_detail',
                                  kwargs={'post_id': self.post.id}
                                  )
        response = self.authorized_client.get(POST_DETAIL_URL)
        first_object = response.context['post']
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.post.group)

    def test_post_edit_correct_context(self):
        """Форма редактируемого поста в шаблоне post_edit сформирована
        с правильным контекстом, отфильтрована по id."""
        POST_EDIT_URL = reverse('posts:post_edit',
                                kwargs={'post_id': self.post.id}
                                )
        response = self.authorized_client.get(POST_EDIT_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_correct_context(self):
        """Форма редактируемого поста в шаблоне post_create
        сформирована с правильным контекстом."""
        response = self.authorized_client.get(POST_CREATE_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_additional_verification_in_another_page(self):
        """Дополнительная проверка при указании группы поста,
        пост появляется на других страницах """
        post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
            group=self.group)
        form_fields = {
            INDEX_URL: post,
            GROUP_LIST_URL: post,
            PROFILE_URL: post,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context.get('page_obj')
                self.assertIn(expected, form_field)

    def test_post_create_additional_verification_not_in_another_group(self):
        """Проверка, что этот пост не попал в группу,
        для которой не был предназначен."""
        form_fields = {
            GROUP_LIST_URL: Post.objects.exclude(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context.get('page_obj')
                self.assertNotIn(expected, form_field)

    def test_clean_cache_index(self):
        """Записи в Index хранятся в кэше и обновляются раз в 20 секунд"""
        request_1 = self.authorized_client.get(INDEX_URL)
        Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
        )
        request_2 = self.authorized_client.get(INDEX_URL)
        self.assertEqual(request_1.content, request_2.content)
        cache.clear()
        request_3 = self.authorized_client.get(INDEX_URL)
        self.assertNotEqual(request_2.content, request_3.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug='test-slug',
            description="Тестовое описание",
        )
        cls.list_url = [INDEX_URL, GROUP_LIST_URL, PROFILE_URL]
        cls.posts = []
        for i in range(1, 14):
            cls.posts.append(
                Post(
                    author=cls.user,
                    text=f'Test post {i} for verification',
                    group=cls.group,
                )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_index_first_page_contains_ten_records(self):
        """Проверка: количество постов на первой странице index равно 10."""
        response = self.client.get(INDEX_URL)
        self.assertEqual(len(response.context['page_obj']), POSTS_ON_THE_PAGE)

    def test_index_second_page_contains_three_records(self):
        """Проверка: на второй странице index должно быть три поста."""
        response = self.client.get(INDEX_URL + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']), POSTS_ON_THE_SECOND_PAGE)

    def test_group_list_first_page_contains_ten_records(self):
        """Проверка: количество постов
        на первой странице group_list равно 10."""
        response = self.client.get(GROUP_LIST_URL)
        self.assertEqual(len(
            response.context['page_obj']), POSTS_ON_THE_PAGE)

    def test_group_list_second_page_contains_three_records(self):
        """Проверка: на второй странице group_list должно быть три поста."""
        response = self.client.get(GROUP_LIST_URL + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']), POSTS_ON_THE_SECOND_PAGE)

    def test_profile_first_page_contains_ten_records(self):
        """Проверка: количество постов на первой странице profile равно 10."""
        response = self.client.get(PROFILE_URL)
        self.assertEqual(len(
            response.context['page_obj']), POSTS_ON_THE_PAGE)

    def test_profile_second_page_contains_three_records(self):
        """Проверка: на второй странице profile должно быть три поста."""
        response = self.client.get(PROFILE_URL + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']), POSTS_ON_THE_SECOND_PAGE)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_follower = User.objects.create_user(
            username='user_follower'
        )
        cls.user_following = User.objects.create_user(
            username='user_following'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_following,
            text='Тестовый текст комментария',
            group=cls.group,
        )
        FollowTests.profile_follow_url = reverse('posts:profile_follow',
                                     kwargs={'username':
                                             cls.user_following.username}
                                     )
        FollowTests.profile_unfollow_url = reverse('posts:profile_unfollow',
                                       kwargs={'username':
                                               cls.user_following.username}
                                       )

    def setUp(self):
        self.auth_client_follower = Client()
        self.auth_client_follower.force_login(self.user_follower)
        self.auth_client_following = Client()
        self.auth_client_following.force_login(self.user_following)

    def test_auth_user_can_follow(self):
        """Авторизованный пользователь может подписываться на автора"""
        self.auth_client_follower.get(self.profile_follow_url)
        count_following = Follow.objects.all().count()
        self.assertEqual(count_following, 1)

    def test_auth_user_can_unfollow(self):
        """Авторизованный пользователь может отписаться от автора"""
        self.auth_client_follower.get(self.profile_follow_url)
        self.auth_client_follower.get(self.profile_unfollow_url)
        count_following = Follow.objects.all().count()
        self.assertEqual(count_following, 0)

    def test_subscription_feed_users(self):
        """Новая запись пользователя появляется в ленте подписчиков
        и не появляется в ленте тех, кто не подписан"""
        Follow.objects.create(
            user=FollowTests.user_follower,
            author=FollowTests.user_following
        )
        response = self.auth_client_follower.get('/follow/')
        posts = response.context['page_obj']
        self.assertEqual(posts[0].text, 'Тестовый текст комментария')
        response = self.auth_client_following.get('/follow/')
        self.assertNotContains(
            response,
            'Тестовый текст комментария'
        )

    def test_not_follow_yourself(self):
        """Проверка, что нельзя подписаться на самого себя"""
        response = self.auth_client_following.get(self.profile_follow_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

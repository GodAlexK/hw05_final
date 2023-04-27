from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post, User

INDEX_URL = reverse('posts:index')
GROUP_LIST_URL = reverse('posts:group_list', kwargs={'slug': 'test-slug'})
PROFILE_URL = reverse('posts:profile', kwargs={'username': 'test-user'})
POST_CREATE_URL = reverse('posts:post_create')
UNEXISTING_URL = '/unexisting_page'


class StaticURLTests(TestCase):
    def test_homepage(self):
        guest_client = Client()
        response = guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test-user')
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
        )
        PostURLTests.post_detail_url = reverse('posts:post_detail',
                                               kwargs={'post_id': cls.post.id}
                                               )
        PostURLTests.post_edit_url = reverse('posts:post_edit',
                                             kwargs={'post_id': cls.post.id}
                                             )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.index_data = (INDEX_URL, 'posts/index.html',
                           self.guest_client,
                           HTTPStatus.OK
                           )
        self.group_list_data = (GROUP_LIST_URL, 'posts/group_list.html',
                                self.guest_client,
                                HTTPStatus.OK
                                )
        self.profile_data = (PROFILE_URL, 'posts/profile.html',
                             self.guest_client,
                             HTTPStatus.OK
                             )
        self.post_detail_data = (self.post_detail_url,
                                 'posts/post_detail.html',
                                 self.guest_client,
                                 HTTPStatus.OK
                                 )
        self.post_create_data = (POST_CREATE_URL, 'posts/create_post.html',
                                 self.authorized_client,
                                 HTTPStatus.OK
                                 )
        self.post_edit_data = (self.post_edit_url, 'posts/create_post.html',
                               self.authorized_client,
                               HTTPStatus.OK
                               )
        self.unexisting_data = (UNEXISTING_URL, None,
                                self.guest_client,
                                HTTPStatus.NOT_FOUND
                                )

    def test_pages_status(self):
        pages = (
            self.index_data,
            self.group_list_data,
            self.profile_data,
            self.post_detail_data,
            self.post_create_data,
            self.post_edit_data,
            self.unexisting_data)
        for url, _, client, status_code in pages:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_posts_post_id_edit_url_exists_at_author(self):
        """Страница /posts/post_id/edit/ доступна только автору."""
        self.user = User.objects.get(username=self.user)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(self.post_edit_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

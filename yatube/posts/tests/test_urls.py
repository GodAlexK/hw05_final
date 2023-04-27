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
        PostURLTests.comment_url = reverse('posts:add_comment',
                                             kwargs={'post_id': cls.post.id}
                                             )
        cls.group_list_data = (GROUP_LIST_URL, 'posts/group_list.html',
                                cls.guest_client,
                                HTTPStatus.OK
                                )
        cls.profile_data = (PROFILE_URL, 'posts/profile.html',
                             cls.guest_client,
                             HTTPStatus.OK
                             )
        cls.post_detail_data = (cls.post_detail_url, 'posts/post_detail.html',
                                 cls.guest_client,
                                 HTTPStatus.OK
                                 )
        cls.post_create_data = (POST_CREATE_URL, 'posts/create_post.html',
                                 cls.authorized_client,
                                 HTTPStatus.OK
                                 )
        cls.comment_data = (cls.comment_url, 'posts:add_comment',
                                 cls.authorized_client,
                                 HTTPStatus.OK
                                 )
        cls.post_edit_data = (cls.post_edit_url, 'posts/create_post.html',
                               cls.authorized_client,
                               HTTPStatus.OK
                               )
        cls.unexisting_data = (UNEXISTING_URL, None,
                                cls.guest_client,
                                HTTPStatus.NOT_FOUND
                                )
        
    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_status(self):
        pages = (
            self.index_data,
            self.group_list_data,
            self.profile_data,
            self.post_detail_data,
            self.post_create_data,
            self.comment_data,
            self.post_edit_data,
            self.unexisting_data)
        for url, _, client, status_code in pages:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_posts_post_id_edit_url_exists_at_author(self):
        """Страница /posts/post_id/edit/ доступна только автору."""
        POST_EDIT_URL = reverse('posts:post_edit',
                                kwargs={'post_id': self.post.id}
                                )
        self.user = User.objects.get(username=self.user)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(POST_EDIT_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

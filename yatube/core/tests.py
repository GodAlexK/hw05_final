from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse

INDEX_URL = reverse('posts:index')
UNEXISTING_URL = '/unexisting_page'


class CustomErrorPagesTest(TestCase):
    def test_404_page(self):
        response = self.client.get(UNEXISTING_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

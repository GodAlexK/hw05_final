from http import HTTPStatus
from django.test import TestCase, Client


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_author_url_exists_at_desired_location(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech_url_exists_at_desired_location(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        template_url_dict = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, address in template_url_dict.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

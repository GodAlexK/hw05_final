from http import HTTPStatus
from django.test import TestCase, Client
from django.urls import reverse


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_about_author_accessible_by_name(self):
        """URL, генерируемый при помощи имени about:author, доступен."""
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_tech_accessible_by_name(self):
        """URL, генерируемый при помощи имени about:tech, доступен."""
        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

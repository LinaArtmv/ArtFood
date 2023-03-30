from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from http import HTTPStatus


User = get_user_model()


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_availability_about_pages(self):
        """Тестирование общедоступных страниц приложения about."""
        context = ['/about/author/',
                   '/about/tech/']
        for address in context:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_about_correct_template(self):
        """URL адрес использует соответствующий шаблон."""
        templates = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/'
        }
        for template, address in templates.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_namespace_about(self):
        """Проверка пространства имен приложения about."""
        templates = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech')}
        for template, reverse_name in templates.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

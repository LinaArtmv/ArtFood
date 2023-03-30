from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus


User = get_user_model()


class UserURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username='NoName')
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)

    def test_availability_users_pages(self):
        """Тестирование общедоступных страниц."""
        context = ['/auth/signup/',
                   '/auth/login/',
                   '/auth/logout/',
                   '/auth/password_reset/',
                   '/auth/password_reset/done/',
                   '/auth/reset/<uidb64>/<token>/',
                   '/auth/password_reset_complete/']
        for address in context:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorised_users_pages(self):
        """Тестирование страниц смены пароля."""
        context = ['/auth/password_change/',
                   '/auth/password_change/done/']
        for address in context:
            with self.subTest(address=address):
                response = self.authorised_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_users_correct_template(self):
        """URL адрес использует соответствующий шаблон."""
        templates = {
            'users/signup.html': '/auth/signup/',
            'users/login.html': '/auth/login/',
            'users/logged_out.html': '/auth/logout/',
            'users/password_reset_form.html': '/auth/password_reset/',
            'users/password_reset_done.html': '/auth/password_reset/done/',
            'users/password_reset_confirm.html':
            '/auth/reset/<uidb64>/<token>/',
            'users/password_reset_complete.html':
            '/auth/password_reset_complete/'}
        for template, address in templates.items():
            with self.subTest(address=address):
                response = self.authorised_client.get(address)
                self.assertTemplateUsed(response, template)

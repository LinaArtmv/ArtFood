from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms


User = get_user_model()


class UserPagesTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username='NoName')
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)

    def test_pages_uses_correct_template_users(self):
        """URL адреса используют соответствующий шаблон."""
        templates = {
            'users/signup.html': reverse('users:signup'),
            'users/login.html': reverse('users:login'),
            'users/logged_out.html': reverse('users:logout'),
            'users/password_reset_form.html': reverse('users:password_reset'),
            'users/password_reset_done.html':
            reverse('users:password_reset_done'),
            'users/password_reset_complete.html':
            reverse('users:password_reset_complete')}
        for template, reverse_name in templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorised_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_signup_page_correct_context(self):
        """Шаблон signup сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('users:signup'))
        form_fields = {'username': forms.fields.CharField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

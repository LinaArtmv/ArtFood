from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()


class TestUserForms(TestCase):
    def setUp(self):
        super().setUp()
        self.guest_client = Client()

    def test_create_user(self):
        """При заполнении формы signup создается пользователь."""
        form_data = {'username': 'NoName',
                     'password1': 'Django_2023',
                     'password2': 'Django_2023'}
        response = self.guest_client.post(reverse('users:signup'),
                                          data=form_data,
                                          follow=True)
        self.assertRedirects(response, reverse('posts:index'))
        self.assertTrue(User.objects.filter(username='NoName').exists())

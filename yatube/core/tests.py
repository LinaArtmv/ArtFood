from django.test import TestCase


class ViewTestClass(TestCase):
    def test_error_pages(self):
        """При ошибке 404 используется кастомный шаблон."""
        response = self.client.get('/group/')
        self.assertTemplateUsed(response, 'core/404.html')
        self.assertEqual(response.status_code, 404)

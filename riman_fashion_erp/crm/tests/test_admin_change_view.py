from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from crm.models import Client


class AdminClientChangeViewTest(TestCase):
    def setUp(self):
        User = get_user_model()
        # create superuser for admin access
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        # create a client instance
        self.crm_client = Client.objects.create(first_name='Test', last_name='User', phone='0123456789')
        # log in as admin
        self.client.force_login(self.admin_user)

    def test_admin_client_change_renders(self):
        """The admin change view for Client should render without raising an AttributeError."""
        url = reverse('admin:crm_client_change', args=[self.crm_client.id])
        response = self.client.get(url)
        # Expect OK response (200). If the AttributeError happens during rendering, test will error.
        self.assertEqual(response.status_code, 200)
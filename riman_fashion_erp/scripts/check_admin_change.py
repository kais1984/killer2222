from django.test import Client
from django.contrib.auth import get_user_model
User = get_user_model()
admin = User.objects.filter(is_superuser=True).first()
if not admin:
    admin = User.objects.create_superuser('admin','admin@example.com','admin')

c = Client()
logged = c.login(username='admin',password='admin')
print('logged', logged)
resp = c.get('/admin/crm/client/1/change/')
print('status', resp.status_code)
print(resp.content[:1000])

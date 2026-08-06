"""Audit dashboard frontend routes."""
import os
import sys

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client

from apps.dashboard.module_config import MODULES

User = get_user_model()
user = User.objects.filter(email='admin@acme.com').first() or User.objects.first()
if not user:
    print('ERROR: No user found. Run seed_data first.')
    sys.exit(1)

client = Client(HTTP_HOST='127.0.0.1')
client.force_login(user)

routes = [
    '/',
    '/dashboard/',
    '/module/reports/',
    '/module/ai/',
]

for mod, cfg in MODULES.items():
    routes.append(f'/module/{mod}/')
    for tab in cfg['tabs']:
        key = tab['key']
        routes.append(f'/module/{mod}/{key}/')
        routes.append(f'/module/{mod}/{key}/create/')

failed = []
for path in routes:
    response = client.get(path)
    if response.status_code not in (200, 302):
        failed.append((path, response.status_code))

print(f'Tested {len(routes)} GET routes as {user.email}')
for path, status in failed:
    print(f'  FAIL {status} {path}')
if not failed:
    print('  All routes returned 200/302')

# Check key template fragments
checks = [
    ('/', b'welcome-banner'),
    ('/module/employees/', b'data-table-card'),
    ('/module/reports/', b'deptReportChart'),
    ('/module/ai/', b'chatMessages'),
]
print('\nTemplate checks:')
for path, needle in checks:
    r = client.get(path)
    ok = needle in r.content
    print(f'  {"OK" if ok else "MISSING"} {path} -> {needle.decode()}')

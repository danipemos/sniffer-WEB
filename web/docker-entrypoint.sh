#!/bin/bash

echo "making migrations"
python manage.py makemigrations

echo "running migrations"
python manage.py migrate

echo "creating superuser"
python manage.py shell <<EOF
from users.models import OurUser
if not OurUser.objects.filter(username='admin').exists():
    OurUser.objects.create_superuser('admin', 'sniffer')
EOF

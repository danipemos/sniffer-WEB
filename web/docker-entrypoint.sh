#!/bin/bash
ip route add 10.8.0.0/24 via 10.8.1.4
echo "making migrations"
python3 manage.py makemigrations users monitorize

echo "migrating"
python3 manage.py migrate

echo "creating superuser"

python manage.py shell <<EOF
from users.models import OurUser
if not OurUser.objects.filter(username='admin').exists():
    OurUser.objects.create_superuser(
        username='admin',
        password='sniffer',)
EOF
daphne -b 0.0.0.0 -p 8000 web.asgi:application
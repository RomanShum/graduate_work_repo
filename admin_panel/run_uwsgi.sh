#!/usr/bin/env bash

set -e

python manage.py compilemessages

python manage.py collectstatic --no-input

python manage.py migrate --no-input

chown www-data:www-data /var/log

uwsgi --strict --ini /etc/app/uwsgi.ini

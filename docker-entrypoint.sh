#!/bin/sh

set -ea

host="$1"
shift

while ! nc -z $host 5432;
do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1;
done;

>&2 echo "Postgres is up - executing command"

python manage.py migrate
python manage.py runserver 0.0.0.0:8000

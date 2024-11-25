#!/bin/bash

./wait-for-it.sh db:5433

python3 manage.py migrate
python3 manage.py collectstatic --noinput
python3 manage.py runserver 0.0.0.0:8000
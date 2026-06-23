#!/usr/bin/env bash
# Script di build per Render
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Popola il database con dati demo ad ogni deploy,
# necessario perché Render usa un filesystem effimero con SQLite.
python manage.py seed_demo

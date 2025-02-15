#!/usr/bin/env bash
# exit on error
set -o errexit

# Move requirements.txt to the correct location if it's not there
if [ ! -f "portofino/requirements.txt" ]; then
    mv requirements.txt portofino/ 2>/dev/null || true
fi

cd portofino
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate 
#!/bin/bash
set -x
flask db upgrade
gunicorn --bind=0.0.0.0 --timeout 300 gwtroll:app

#!/bin/bash
set -x
#flask db upgrade
gunicorn -w 3 --bind=0.0.0.0 --timeout 600 gwtroll:app --error-logfile '-'

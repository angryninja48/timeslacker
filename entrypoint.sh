#!/bin/sh
#LOG_FOLDER="/var/logs"

if [ -n "$LOG_FOLDER" ]; then
    ACCESS_LOG=${LOG_FOLDER}/access.log
    ERROR_LOG=${LOG_FOLDER}/error.log
else
    ACCESS_LOG=-
    ERROR_LOG=-
fi

exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --env SCRIPT_NAME=/slack \
    --access-logfile "$ACCESS_LOG" \
    --error-logfile "$ERROR_LOG" \
     main:app
"$@"

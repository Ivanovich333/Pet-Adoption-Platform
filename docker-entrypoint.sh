set -e

if [ "$DATABASE_ENGINE" = "django.db.backends.postgresql" ]; then
    echo "Waiting for PostgreSQL..."
    while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
        sleep 0.1
    done
    echo "PostgreSQL started"
fi

echo "Applying database migrations..."
python manage.py migrate

if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput

if [ "$1" = "gunicorn" ]; then
    echo "Starting Gunicorn server..."
    exec gunicorn pet_adoption.wsgi:application --bind 0.0.0.0:8000
else
    echo "Starting development server..."
    exec python manage.py runserver 0.0.0.0:8000
fi 
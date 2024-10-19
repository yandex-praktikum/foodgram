cd project/
# python manage.py runserver 0.0.0.0:8000
python manage.py makemigrations --noinput
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py import_ingredients ./../data/ingredients.csv
python manage.py import_tags ./../data/tags.csv
gunicorn project.wsgi:application --bind 0:8000


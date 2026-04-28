FROM python:3.12-alpine
ENV DJANGO_SETTINGS_MODULE=Apka_muzyczna.settings
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["sh", "-c", "mkdir -p music/static/media music/static/tekst && python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]

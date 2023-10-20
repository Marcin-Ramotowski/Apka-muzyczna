FROM python:3.12.0rc2-alpine3.18
ENV DJANGO_SETTINGS_MODULE=Apka_muzyczna.settings
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD python manage.py runserver 0.0.0.0:8000

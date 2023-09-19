FROM python:3.12.0rc2-alpine3.18
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD python manage.py runserver
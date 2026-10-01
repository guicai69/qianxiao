FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate && gunicorn -c gunicorn.conf.py -b 0.0.0.0:8000 config.wsgi:application"]

FROM python:3.13.0-alpine3.20
ADD ./api /app
WORKDIR /app
ADD requirements.txt /
RUN apk add --no-cache git
RUN pip install -r /requirements.txt

EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:create_app()", "--access-logfile", "-" ]

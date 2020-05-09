FROM docker.io/python:3.7
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5001
CMD ["gunicorn"  , "-b", "0.0.0.0:8080", "wsgi:application"]

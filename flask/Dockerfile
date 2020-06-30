FROM python:3.8.3-slim-buster
COPY . /app
WORKDIR /app
RUN apt update && apt install -y apt-utils
RUN apt-get install -y libglib2.0-0
RUN python -m pip install -r requirements.txt
EXPOSE 8080
CMD ["gunicorn"  , "-b", "0.0.0.0:8080", "wsgi:application"]

FROM ghcr.io/90victor09/ahri/base:latest

RUN pip3 install uwsgi==2.0.21

COPY . /app
WORKDIR /app

RUN pip3 install -e /app

EXPOSE 5000
CMD uwsgi \
    --http 0.0.0.0:5000 \
    --thunder-lock \
    --single-interpreter \
    --enable-threads \
    --processes=${UWSGI_WORKERS:-2} \
    --buffer-size=8192 \
    --max-requests=1000 \
    --wsgi-file /app/app/wsgi.py

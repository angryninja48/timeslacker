FROM python:3.8-alpine3.12 as build

RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/

# Install Build Deps and Chrome
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.12/main" >> /etc/apk/repositories \
    && echo "http://dl-4.alpinelinux.org/alpine/v3.12/community" >> /etc/apk/repositories \
    && apk update \
    && apk add --virtual build-deps gcc build-base python3-dev \
    && apk add chromium chromium-chromedriver \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && apk del build-deps

FROM build as base

COPY app.py /app/
COPY main.py /app/
COPY entrypoint.sh /app/

WORKDIR /app

EXPOSE 8000
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

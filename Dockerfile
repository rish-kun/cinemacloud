FROM python:3.13.0-alpine3.19
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV PATH="/scripts:${PATH}"

COPY ./requirements.txt ./requirements.txt
RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN apk del .tmp
RUN mkdir /app 

COPY ./server /app
WORKDIR /app
COPY ./scripts /scripts
RUN chmod +x /scripts/*

# RUN python3 manage.py collectstatic --noinput
RUN python3 manage.py makemigrations 

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

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

RUN adduser -D user
RUN chown -R user:user /vol/
RUN chmod -R 755 /vol/web
# USER user


EXPOSE 8000
# RUN python3 manage.py collectstatic --noinput
CMD [ "entrypoint.sh" ]
RUN python3 manage.py makemigrations 
# RUN python3 manage.py migrate


# CMD [ "python3", "manage.py", "runserver", "0.0.0.0:8000" ]
FROM python:3.8.5-alpine3.12 AS base

WORKDIR /usr/app

RUN apk update && apk add gcc libc-dev linux-headers zlib-dev jpeg-dev libjpeg

ADD . .

RUN pip3 install -r ./requirements.txt

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]

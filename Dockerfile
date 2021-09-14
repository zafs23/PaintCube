FROM python:3.7-alpine
MAINTAINER Sajia Zafreen

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
# need to add some dependencies to install the package for
# django to communicate with postgres
RUN apk add --update --no-cache postgresql-client
# apk is the name of the package manager that comes with Alpine, other is
# in the notes
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev
# need to install some temporary packages that need to be installed to
# run the requirements and later it can be removed
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps
# remove by the alias 

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D user
USER user

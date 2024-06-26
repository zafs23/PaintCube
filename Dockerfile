FROM python:3.7-alpine
MAINTAINER Sajia Zafreen

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
# need to add some dependencies to install the package for
# django to communicate with postgres
# for Pillow added jpeg-dev
RUN apk add --update --no-cache postgresql-client jpeg-dev
# apk is the name of the package manager that comes with Alpine, other is
# in the notes
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
# need to install some temporary packages that need to be installed to
# run the requirements and later it can be removed
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps
# remove by the alias

RUN mkdir /app
WORKDIR /app
COPY ./app /app

# the /vol is a subdirectory that shares files with other containers
RUN mkdir -p /vol/web/media
# two files holds the static data , static is for JS, css files
RUN mkdir -p /vol/web/static
RUN adduser -D user
# change the owenership, we have to give persmissions to access the files
# while we are in the root user
RUN chown -R user:user /vol/
# the owner can do anything to the directory, and rest can read and execute
# from the directory
RUN chmod -R 755 /vol/web
USER user

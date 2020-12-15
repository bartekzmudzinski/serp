FROM python:3
LABEL author=BartłomiejŻmudziński

ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python-psycopg2 && \
    apt-get install -y python3-pip && \
    apt-get install -y netcat && \
    apt-get clean

RUN pip3 install pip --upgrade && \
    pip install psycopg2-binary \
    pip install psycopg2

COPY ./requirements.txt ./
RUN pip3 install -r ./requirements.txt

COPY ./docker-entrypoint.sh ./
RUN chmod u+x docker-entrypoint.sh

WORKDIR /app/src
VOLUME ["/app/src"]

EXPOSE 8000

ENV PYTHONPATH=$(pwd):/usr/local/lib/python3.8/site-packages:/usr/local/lib/python2.7/site-packages
ENV DJANGO_SETTINGS_MODULE=core.settings

CMD /docker-entrypoint.sh db

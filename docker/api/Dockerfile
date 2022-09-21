FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1



RUN apt-get update \
  && apt-get -y install netcat gcc postgresql \
  && apt-get clean


WORKDIR /test/src

COPY . /test/
COPY requirements.txt /test/src

RUN pip install -r requirements.txt

EXPOSE 8000

FROM python:slim-buster

LABEL maintainer Sasha Alimov <klimdos@gmail.com>

WORKDIR /app

COPY src/requirements.txt .

RUN pip install -r requirements.txt

COPY src/app.py .

ENTRYPOINT ["sh", "-c", "python app.py"]

FROM python:3.9-slim-bullseye

WORKDIR /home/smbirch/code/indoorweather

COPY Pipfile Pipfile.lock ./

RUN pip install pipenv && pipenv install --system

COPY . .

EXPOSE 8086

CMD python app.py
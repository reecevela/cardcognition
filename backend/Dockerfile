FROM python:3.8-slim-buster

# set work directory
WORKDIR /app

ADD . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

CMD /wait-for-it.sh db:5432 -- gunicorn -b 0.0.0.0:8000 app:app
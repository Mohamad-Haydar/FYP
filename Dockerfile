FROM python:3.10.6-slim-buster

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD [ "python3", "main.py" ]
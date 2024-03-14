FROM python:3.8.18

WORKDIR /app

COPY . .

RUN pip install confluent_kafka flask numpy

EXPOSE 5001

CMD ["python", "app.py"]

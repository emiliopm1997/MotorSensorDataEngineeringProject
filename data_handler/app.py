from confluent_kafka import Consumer
from flask import Flask
from pathlib import Path

import pandas as pd

from .data_base import AbstractDBHandler, DataLakeHandler

app = Flask(__name__)

KAFKA_SERVER = 'kafka:9092'
TOPIC = 'motor_voltage'
DL_PATH = Path('data/raw_data.db')


@app.route('/save_raw_data', methods=['GET'])
def save_raw_data():
    db = DataLakeHandler(DL_PATH)
    table_name = "MOTOR_READINGS"

    consumer = Consumer(TOPIC, bootstrap_servers=[KAFKA_SERVER])

    for _ in range(5):
        msg = consumer.poll(max_records=1000)
        data = pd.DataFrame(msg.value.decode())
        data.to_sql(table_name, db.conn, if_exists="append", index=False)
    return "Consumer started!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)

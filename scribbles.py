from confluent_kafka import Producer, Consumer
import sys
import json

import pandas as pd

# Kafka broker address
bootstrap_servers = 'localhost:9092'

# Kafka topic
topic = 'my_topic'

# Kafka producer configurationq
producer_config = {
    'bootstrap.servers': bootstrap_servers
}

# Kafka consumer configuration
consumer_config = {
    'bootstrap.servers': bootstrap_servers,
    'group.id': 'my_consumer_group',
    'auto.offset.reset': 'earliest'
}

# Function to produce messages to Kafka
def kafka_producer():
    print("establishing producer")
    p = Producer(producer_config)
    print("producer established")
    try:
        # Produce messages
        for i in range(1, 10):
            data = pd.DataFrame(
                {"example": [1, 2, 3], "example2": ["a", "b", "c"]}
            )
            message = data.to_dict("records")
            print(f"sending {i} data")
            p.produce(topic, json.dumps(message).encode())
            p.flush()
            print(f"Produced {i}")
    except KeyboardInterrupt:
        sys.stderr.write('%% Aborted by user\n')
    finally:
        p.flush()
        p.close()

# Function to consume messages from Kafka
def kafka_consumer():
    c = Consumer(consumer_config)
    c.subscribe([topic])
    try:
        # Consume messages
        for _ in range(10):
            msg = c.poll(max_records=2)
            if msg is None:
                return
            if msg.error():
                print("Consumer error: {}".format(msg.error()))
                continue
            print('Consumed message: {}'.format(msg.value().decode('utf-8')))
    except KeyboardInterrupt:
        sys.stderr.write('%% Aborted by user\n')
    finally:
        c.close()


if __name__ == '__main__':
    # Run Kafka producer and consumer
    kafka_producer()
    # kafka_consumer()

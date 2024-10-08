import json

from confluent_kafka.cimpl import Producer


def get_producer():
    producer = Producer({
        'bootstrap.servers': 'localhost:9092',
        'client.id': 'login-producer'
    })
    return producer


def send_message(topic, message, callback=None):
    producer = get_producer()

    key = str(message['user_id'])
    value = json.dumps(message)

    producer.produce(topic, key=key, value=value, callback=callback)
    producer.flush()

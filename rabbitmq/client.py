from rabbitmq.constants import CV_REVIEW_RESULTS, CV_REVIEW_TASKS
from utils.config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_PORT, RABBITMQ_USER
import pika

RABBITMQ_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"

params = pika.URLParameters(RABBITMQ_URL)
connection = pika.BlockingConnection(params)
mq_channel = connection.channel()

mq_channel.queue_declare(queue=CV_REVIEW_TASKS, durable=True)
mq_channel.queue_declare(queue=CV_REVIEW_RESULTS, durable=True)
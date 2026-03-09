from rabbitmq.client import mq_channel
from rabbitmq.constants import CV_REVIEW_TASKS
from services.cv_review import cv_review_callback
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def main():
    print("Waiting for tasks...")
    mq_channel.basic_qos(prefetch_count=1)
    mq_channel.basic_consume(queue=CV_REVIEW_TASKS,
                             on_message_callback=cv_review_callback)

    mq_channel.start_consuming()


if __name__ == "__main__":
    main()

import json
from db.database import SessionLocal
from models.cv_feedback import CVFeedback
import time
from rabbitmq.client import mq_channel
from rabbitmq.constants import CV_REVIEW_RESULTS
import pika


def process_cv_task(body):
    # Debug
    data = json.loads(body)
    print(f"Processing: {data}")

    # Get Feedback from AI
    feedback = "This Portfolio Sucks"
    file_link = data["file_uri"]
    user_id = data["user_id"]

    # DB
    db = SessionLocal()
    cv_feedback = CVFeedback(
        user_id=user_id,
        file_link=file_link,
        feedback=feedback
    )
    db.add(cv_feedback)
    db.commit()
    db.refresh(cv_feedback)

    # Publish Event
    time.sleep(5)
    print(f"Task done: {data}")
    mq_channel.basic_publish(
        exchange='',
        routing_key=CV_REVIEW_RESULTS,
        body=json.dumps({
            "cv_result": "updated",
            "id": cv_feedback.id
        }),
        properties=pika.BasicProperties(
            delivery_mode=2,
        )
    )


def cv_review_callback(ch, method, properties, body):
    ch.basic_ack(delivery_tag=method.delivery_tag)

import json
from db.database import SessionLocal
from models.cv_feedback import CVFeedback
from models.user import User
from models.user_token import UserToken

import time
from rabbitmq.client import mq_channel
from rabbitmq.constants import CV_REVIEW_RESULTS
import pika
import logging

logger = logging.getLogger(__name__)


def process_cv_task(body):
    # Debug
    data = json.loads(body)
    logger.info(f"Processing: {data}")

    # Get Feedback from AI
    feedback = "This Portfolio Sucks"
    id = data["id"]

    # DB
    db = SessionLocal()
    try:
        cv_feedback = db.query(CVFeedback).filter(CVFeedback.id == id).first()

        if cv_feedback:
            cv_feedback.feedback = feedback
            cv_feedback.status = "finished"
            db.commit()
            db.refresh(cv_feedback)
            logger.info(f"CVFeedback {id} updated")

            # Publish Event
            time.sleep(5)
            logger.info(f"Task done: {data}")
            mq_channel.basic_publish(
                exchange='',
                routing_key=CV_REVIEW_RESULTS,
                body=json.dumps({
                    "cv_result": "updated",
                    "id": id
                }),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                )
            )
        else:
            logger.warning(f"CVFeedback {id} not found")

    finally:
        pass


def cv_review_callback(ch, method, properties, body):
    process_cv_task(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

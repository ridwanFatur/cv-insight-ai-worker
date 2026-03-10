import json
import time
from sqlalchemy import text
from ai_services.cv_feedback_analysis import get_feedback
from db.database import get_connection

from rabbitmq.channel import channel
from rabbitmq.constants import CV_REVIEW_RESULTS
import pika
import logging

logger = logging.getLogger(__name__)


def process_cv_task(body):
    # Debug
    data = json.loads(body)
    logger.info(f"Processing: {data}")

    # Get Feedback from AI
    cv_id = data["id"]
    user_id = data["user_id"]
    file_link = data["file_link"]
    feedback = get_feedback(file_link)

    with get_connection() as conn:
        select_query = text(
            "SELECT id FROM cv_feedbacks WHERE id = :id LIMIT 1")
        result = conn.execute(select_query, {"id": cv_id}).first()
        if result:
            update_query = text("""
                UPDATE cv_feedbacks
                SET feedback = :feedback, status = :status
                WHERE id = :id
            """)
            conn.execute(update_query, {
                         "feedback": feedback, "status": "finished", "id": cv_id})
            conn.commit()
            logger.info(f"CVFeedback {cv_id} updated")

            # Publish Event
            logger.info(f"Task done: {data}")
            channel.basic_publish(
                exchange='',
                routing_key=CV_REVIEW_RESULTS,
                body=json.dumps({
                    "type": "cv_updated",
                    "id": cv_id,
                    "user_id": user_id,
                    "feedback": feedback,
                }),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                )
            )
        else:
            logger.warning(f"CVFeedback {cv_id} not found")


def cv_review_callback(ch, method, properties, body):
    try:
        process_cv_task(body)
    except Exception as e: 
        logger.error(f"{e}")
        pass
    ch.basic_ack(delivery_tag=method.delivery_tag)

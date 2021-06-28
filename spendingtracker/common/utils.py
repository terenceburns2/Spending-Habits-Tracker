from flask import flash
from spendingtracker.models import Message
from spendingtracker import db
from datetime import datetime


def flash_message(content, type, user_id):
    """
    Flash a message and add that message into database.
    :param content: flash message content
    :param type: flash message type, e.g. 'success', 'danger', 'info'
    :param user_id: user id
    :return: None
    """
    flash(content, type)
    time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    message = Message(content=content, type=type, timestamp=datetime.strptime(time, "%Y-%m-%d %H:%M:%S"), user_id=user_id)
    db.session.add(message)
    db.session.commit()


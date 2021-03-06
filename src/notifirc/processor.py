import logging

from notifirc.utils import zero_min
from notifirc.message import Message

CONTEXT_AFTER = 5

logger = logging.getLogger(__name__)


def check_matches(msg, filters):
    matched_filters = []
    for f in filters:
        if f['func'](msg):
            matched_filters.append(f['id'])
    return matched_filters


def get_context(msg_store, channel, msg_id, m_after=5, m_before=2):
    first_msg_id = zero_min(msg_id - m_before)
    last_msg_id = msg_id + m_after
    msg_ids = list(range(first_msg_id, last_msg_id))
    return msg_store.get_messages(channel, msg_ids)


def process_messages(msg_store, sub, filters, match_writer):

    logger.info("started processor")
    last_msg = 0

    for m in sub.listen():
        msg_data = m['data']
        msg = Message.decode(msg_data)
        last_msg = msg.msg_id

        logger.info(msg.text)

        msg_store.save_message(msg)

        # check msg from the past, so we have some
        # context for our matches
        msg_to_check = msg_store.get_message(msg.channel, last_msg - 5)

        if msg_to_check:
            matches = check_matches(msg_to_check.text, filters)
            if len(matches) > 0:
                match_context = get_context(
                    msg_store, msg_to_check.channel, msg_to_check.msg_id)
                match_writer.save(
                    msg_to_check.channel,
                    matches,
                    match_context)

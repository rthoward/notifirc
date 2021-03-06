import redis
import psycopg2
import logging

from notifirc.subscriber import RedisSubscriber
from notifirc.filters import initialize_filters
from notifirc.message_store import RedisMessageStore
from notifirc.processor import process_messages
from notifirc.match_writer import PostgresMatchWriter

logging.basicConfig(
    format='[%(levelname)s] %(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.DEBUG)


def create_redis():
    return redis.StrictRedis(host='localhost', port=6379)


create_redis().flushall()
sub = RedisSubscriber(create_redis())
m_store = RedisMessageStore(
        redis.StrictRedis(host='localhost', port=6379, decode_responses=True))
db_conn = psycopg2.connect(open('../data/db_uri.txt', 'r').read().rstrip())
filters = initialize_filters(db_conn)
m_writer = PostgresMatchWriter(db_conn)

process_messages(m_store, sub, filters, m_writer)

db_conn.close()

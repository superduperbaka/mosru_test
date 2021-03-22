import logging
import random
import string
import time

from rabbit_client import SyncRabbitProducerDurable
from schemas import MiscSettings, RabbitMQSettings


def emulate_some_work():
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(1, 20)))


def run_consumer(
        host: str,
        port: int,
        v_host: str,
        user: str,
        password: str,
        task_queue: str,
):

    producer = SyncRabbitProducerDurable()
    producer.init_conn(
        host=host,
        port=port,
        v_host=v_host,
        user=user,
        password=password,
        task_queue=task_queue,
    )
    while True:
        try:
            producer.produce(bytes(emulate_some_work(), encoding='utf8'))
            time.sleep(1)
        except KeyboardInterrupt:
            logging.warning('^C detected. Bye.')
            producer.close_conn()
            break


if __name__ == '__main__':
    misc_settings = MiscSettings()
    logging.basicConfig(level=misc_settings.log_level.value)

    rabbit_settings = RabbitMQSettings()
    run_consumer(**rabbit_settings.dict())

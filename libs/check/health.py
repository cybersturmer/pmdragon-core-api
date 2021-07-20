from django.db import connections
from django.db.utils import OperationalError
from django.conf import settings

import celery
import celery.bin.base
import celery.bin.celery
import celery.platforms

import socket


class Health:
    @staticmethod
    def check_database():
        connection = connections['default']

        try:
            _ = connection.cursor()
        except OperationalError:
            return False
        else:
            return True

    @staticmethod
    def __extract_redis_host_port_from_string(string: str):
        if type(string) is not str:
            return False

        """
        By taken this: redis://:some@some.eu-west-1.compute.amazonaws.com:13299
        We return this: (some.eu-west-1.compute.amazonaws.com, 13299)
        """
        host_port_string = string.split('@')[1]
        return host_port_string.split(':')

    @staticmethod
    def check_redis():
        redis_url = settings.REDIS_CONNECTION

        redis_url_type_decision_tree = {
            type(redis_url) is tuple:
                redis_url,
            type(redis_url) is str:
                Health.__extract_redis_host_port_from_string(redis_url)
        }

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.connect(redis_url_type_decision_tree[True])
            s.shutdown(2)
        except OSError:
            return False
        else:
            return True

    @staticmethod
    def get_overall_status() -> dict:
        database = Health.check_database()
        sockets = Health.check_redis()

        ok = all([database, sockets])

        return {
            'ok': ok
        }

from contextlib import contextmanager  # noqa

import redis

import pytest

from bluesky.tests.conftest import RE  # noqa
from bluesky_kafka import BlueskyConsumer  # noqa
from bluesky_kafka.tests.conftest import (  # noqa
    pytest_addoption,
    kafka_bootstrap_servers,
    broker_authorization_config,
    consume_documents_from_kafka_until_first_stop_document,
    temporary_topics,
)
from ophyd.tests.conftest import hw  # noqa

from nslsii.md_dict import RunEngineRedisDict


def pytest_addoption(parser):
    parser.addoption(
        "--xs3-data-dir", action="store", help="path to directory where xspress3 writes data files"
    )

    parser.addoption(
        "--xs3-pv-prefix", action="store", help="PV prefix for xspress3, for example `XF:05IDD-ES{Xsp:1}:`"
    )


@pytest.fixture
def xs3_data_dir(request):
    return request.config.getoption("--xs3-data-dir")


@pytest.fixture
def xs3_pv_prefix(request):
    return request.config.getoption("--xs3-pv-prefix")


@pytest.fixture
def redis_dict_factory():
    """
    Return a "fixture as a factory" that will build identical RunEngineRedisDicts.
    Before the factory is returned, the Redis server will be cleared.

    The factory builds only RunEngineRedisDict instances for a Redis server running
    on localhost:6379, db=0.

    If "host", "port", or "db" are specified as kwargs to the factory function
    an exception will be raised.
    """
    redis_server_kwargs = {
        "host": "localhost",
        "port": 6379,
        "db": 0,
    }

    redis_client = redis.Redis(**redis_server_kwargs)
    redis_client.flushdb()

    def _factory(**kwargs):
        disallowed_kwargs_preset = set(redis_server_kwargs.keys()).intersection(
            kwargs.keys()
        )
        if len(disallowed_kwargs_preset) > 0:
            raise KeyError(
                f"{disallowed_kwargs_preset} given, but 'host', 'port', and 'db' may not be specified"
            )
        else:
            kwargs.update(redis_server_kwargs)

        return RunEngineRedisDict(**kwargs)

    return _factory

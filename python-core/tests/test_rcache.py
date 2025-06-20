import pytest

from src.db.rcache import RCache
from src.os.env import Env

# This test assumes that a redis server is running locally,
# such as in WSL.

# pytest -v tests/test_rcache.py


@pytest.mark.skip(reason="this test is currently disabled")
def test_ping_and_client():
    host = Env.redis_host()
    port = Env.redis_port()
    r = RCache(host, port)
    p = r.ping()
    assert p is True
    assert r.client().ping() is True


@pytest.mark.skip(reason="this test is currently disabled")
def test_get_and_set():
    host = Env.redis_host()
    port = Env.redis_port()
    value = "Miles-{}".format(Env.epoch())
    r = RCache(host, port)
    r.set("CAT", value)

    assert value == r.get("CAT").decode("utf-8")
    assert r.get("not-there") is None

    assert value == r.get_str("CAT")
    assert r.get_str("Dog") is None

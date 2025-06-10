import pytest

from src.os.env import Env
from src.db.mongo_util import MongoUtil

# pytest -v tests/test_mongo.py

@pytest.mark.skip(reason="TODO - enable this test")
def test_vcore():
    conn_string = Env.var("AZURE_COSMOSDB_MONGO_VCORE_CONN_STR")
    if True:
        opts = dict()
        opts["conn_string"] = Env.mongodb_conn_str()
        m = MongoUtil(opts)
        dblist = m.list_databases()
        assert len(dblist) > 0
        if "dev" in dblist:
            m.set_db("dev")
            colls = m.list_collections()
            assert len(colls) > 0

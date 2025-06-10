import asyncio
import pytest

from src.os.env import Env
from src.io.fs import FS
from src.db.cosmos_nosql_util import CosmosNoSqlUtil
from src.util.data_gen import DataGenerator

# pytest -v tests/test_cosmos.py

# This method runs once at the beginning of this test module.
@pytest.fixture(scope="session", autouse=True)
def setup_before_all_tests():
    Env.set_unit_testing_environment()

@pytest.fixture
async def cosmos_util():
    e1 = Env.epoch()
    opts = dict()
    opts["url"] = Env.cosmosdb_nosql_uri()
    opts["key"] = Env.cosmosdb_nosql_key()
    cosmos_util = CosmosNoSqlUtil(opts)
    await cosmos_util.initialize()
    print("#cosmos_util fixture initialized")
    cosmos_util
    # the above is the test 'setup' logic

    yield cosmos_util  # <-- control is passed to the test here

    # the following is the test 'teardown' logic
    databases = await cosmos_util.list_databases()
    for dbname in databases:
        if dbname.startswith("test_db"):
            await cosmos_util.delete_database(dbname)
    await cosmos_util.close()
    e2 = Env.epoch()
    print("#cosmos_util fixture; elapsed: {}".format(e2 - e1))

def create_random_document(id = None, pk = None):
    dg = DataGenerator()
    return dg.random_person_document(id, pk)

@pytest.mark.asyncio
async def test_all(cosmos_util):
    dbname, cname = "dev", "test"
    print("test_all - dbname: {}, cname: {}".format(dbname, cname))

    s = str(type(cosmos_util))
    await asyncio.sleep(0.01)
    assert s == "<class 'src.db.cosmos_nosql_util.CosmosNoSqlUtil'>"

    # test expected failures before db or container is set, or operatons executed
    assert cosmos_util.last_response_headers() == dict()
    assert cosmos_util.last_request_charge() == -1
    assert await cosmos_util.delete_database("does_not_exist") == False
    #assert await cosmos_util.delete_container("does_not_exist") == False

    # test create_database
    b = await cosmos_util.create_database(dbname, 1000)
    databases = await cosmos_util.list_databases()
    print("databases after creation: {}".format(databases))
    assert str(type(databases)) == "<class 'list'>"
    assert dbname in databases

    # test get_database_link, get_current_dbname, and get_database_throughput
    cosmos_util.set_db(dbname)
    link = cosmos_util.get_database_link()
    expected = "dbs/{}".format(dbname)  # dbs/dev
    assert link == expected
    assert cosmos_util.get_current_dbname() == dbname
    throughput = await cosmos_util.get_database_throughput()
    print("throughput: {}".format(throughput))
    # assert throughput['offer_throughput'] >= 1000
    # assert throughput['offer_throughput'] <= 10000

    # test create_container, set_container, list_containers, and get_current_cname
    containers = await cosmos_util.list_containers()
    assert len(containers) < 10
    await cosmos_util.create_container(cname, 1000, "/pk")
    cosmos_util.set_container(cname)
    containers = await cosmos_util.list_containers()
    assert len(containers) > 0
    assert cname in containers
    assert cosmos_util.get_current_cname() == cname

    # test get_container_properties
    props = await cosmos_util.get_container_properties()
    assert (str(type(props))) == "<class 'dict'>"
    FS.write_json(props, "tmp/test_cosmos_util_get_container_properties.json")
    assert '_self' in props.keys()
    assert '_etag' in props.keys()
    assert '_ts' in props.keys()
    assert props["id"] == cname
    assert props["partitionKey"] =={ "kind": "Hash", "paths": [ "/pk" ], "version": 2 }

    # test get_container_link
    link = cosmos_util.get_container_link()
    assert link == 'dbs/dev/colls/test'

    # test get_container_throughput
    #throughput = await cosmos_util.get_container_throughput()  # TODO - fails

    # test create_item, last_response_headers, and last_request_charge
    results = list()
    for n in range(5):
        result = dict()
        obj = create_random_document()
        result['obj'] = obj
        doc = await cosmos_util.create_item(obj)
        result['doc'] = doc
        print(doc)
        assert obj["email"] == doc["email"]
        assert '_etag' in doc.keys()
        assert '_ts' in doc.keys()
        headers = cosmos_util.last_response_headers()
        result['headers'] = headers
        assert (str(type(headers))) == "<class 'dict'>"
        result['ru'] = cosmos_util.last_request_charge()
        results.append(result)
    FS.write_json(results, "tmp/test_cosmos_util_create_item_results.json")

    # test count_documents
    count_result = await cosmos_util.count_documents()
    print("count result: {}".format(count_result))
    assert (str(type(count_result))) == "<class 'list'>"
    assert len(count_result) == 1
    assert (str(type(count_result[0]))) == "<class 'int'>"
    count1 = count_result[0]
    assert count1 > 0

    # test delete_item
    doc = results[0]["doc"]
    delete_result = await cosmos_util.delete_item(doc['id'], doc['pk'])
    print("delete result: {}".format(delete_result))
    count_result = await cosmos_util.count_documents()
    count2 = count_result[0]
    assert count2 == (count1 - 1)

    # test upsert_item
    await asyncio.sleep(1)
    app_update_epoch = Env.epoch()
    doc = results[1]["doc"]
    ts1 = results[1]["doc"]["_ts"]
    doc['app_update_epoch'] = app_update_epoch
    upsert_doc = await cosmos_util.upsert_item(doc)
    print("upsert_doc: {}".format(upsert_doc))
    ts2 = upsert_doc["_ts"]
    assert upsert_doc["app_update_epoch"] == app_update_epoch
    assert ts2 > ts1

    # test point_read on the doc just upserted
    point_read_result = await cosmos_util.point_read(
        upsert_doc['id'], upsert_doc['pk'])
    assert point_read_result["app_update_epoch"] == app_update_epoch

    # test query_items on the just upserted doc
    sql = "select * from c where c.app_update_epoch = {}".format(app_update_epoch)
    docs = await cosmos_util.query_items(
        sql, cross_partition=True, pk="/pk", max_items=100)
    print("docs: {}".format(docs))
    assert len(docs) == 1
    assert docs[0]['app_update_epoch'] == app_update_epoch

    # query all items and write them to a tmp file for visual verification
    sql = "select * from c"
    docs = await cosmos_util.query_items(
        sql, cross_partition=True, pk="/pk", max_items=100)
    FS.write_json(docs, "tmp/test_cosmos_util_query_all_docs.json")

    # test parameterized_query
    sql_template = "SELECT * FROM c WHERE c.id = @id"
    sql_parameters = [
        {"name": "@id", "value": docs[0]['id']}
    ]
    docs = await cosmos_util.parameterized_query(
        sql_template=sql_template,
        sql_parameters=sql_parameters,
        cross_partition=True,
        pk="/pk",
        max_items=100)
    assert len(docs) == 1

    # test execute_item_batch
    # but first find and delete the 'bulk_pk'
    sql = "select * from c where c.pk = 'bulk_pk'"
    coordinates = dict()
    docs = await cosmos_util.query_items(sql, cross_partition=True, pk="/pk", max_items=100)
    for doc in docs:
        id, pk = doc['id'], doc['pk']
        coordinates[id] = pk
    for id in coordinates.keys():
        pk = coordinates[id]
        await cosmos_util.delete_item(id, pk)
    docs = await cosmos_util.query_items(sql, cross_partition=True, pk="/pk", max_items=100)
    assert len(docs) == 0

    if True:
        operations, pk = list(), "bulk_pk"
        for n in range(3):
            op = ("create", (create_random_document(None, pk),))
            operations.append(op)
        results = await cosmos_util.execute_item_batch(operations, pk)
        for idx, result in enumerate(results):
            print("batch result {}: {}".format(idx, result))
        sql = "select * from c where c.pk = 'bulk_pk'"
        docs = await cosmos_util.query_items(
            sql, cross_partition=True, pk="/pk", max_items=100)
        assert len(docs) == 3

    #pytest.fail("intentional fail")

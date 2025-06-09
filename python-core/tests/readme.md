# pytest notes

## Setup and Teardown with @pytest.fixture

This method runs once at the beginning of this test module.

```
@pytest.fixture(scope="session", autouse=True)
def setup_before_all_tests():
    Env.set_unit_testing_environment()
```

### yield

Note how the fixtue name 'sending_user' is injected into the test method.

The part before the yield statement is the 'setup', the part after
the yield statement is the 'teardown' part.

```
@pytest.fixture
def epoch_fixture():
    e1 = Env.epoch()
    print("#epoch_fixture; e1 is: {}".format(e1))
    yield e1
    e2 = Env.epoch()
    print("#epoch_fixture; elapsed: {}".format(e2 - e1))

def test_explore_fixture(epoch_fixture):
    print("#test_explore_fixture; epoch_fixture is: {}".format(epoch_fixture))
    assert epoch_fixture < 1

Output:

---------- Captured stdout setup ----------
#epoch_fixture; e1 is: 1742324453.2284179
---------- Captured stdout call -----------
#test_explore_fixture; epoch_fixture is: 1742324453.2284179
---------- Captured stdout teardown ----------
#epoch_fixture; elapsed: 0.07351374626159668
```

## Annontations

### @pytest.mark.skip annotation

```
import pytest 


@pytest.mark.skip(reason="TODO - enable this test"
def test_nosql_connect():
    ...

```

### @pytest.mark.asyncio annotation

```
import pytest 


@pytest.mark.asyncio
async def test_read_cosmosdb_document():
    ....

```
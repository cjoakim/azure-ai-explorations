from src.io.fs import FS
from src.util.tz import Tz

# pytest -v tests/test_tz.py


def test_common_timezone_list():
    zones = Tz.common_timezone_list()
    FS.write_json(zones, "tmp/common_timezone_list.json")
    expected = 432
    assert len(zones) > (expected - 10)
    assert len(zones) < (expected + 10)
    assert "GMT" in zones


def test_all_timezones():
    zones = Tz.all_timezones()
    FS.write_json(zones, "tmp/all_timezones.json")
    expected = 596
    assert len(zones) > (expected - 10)
    assert len(zones) < (expected + 10)
    assert "GMT" in zones


def test_specific_timesones():
    zone = Tz.gmt_tz()
    assert str(type(zone)) == "<class 'pytz.tzfile.GMT'>"

    zone = Tz.paris_tz()
    assert str(type(zone)) == "<class 'pytz.tzfile.Europe/Paris'>"

    zone = Tz.tokyo_tz()
    assert str(type(zone)) == "<class 'pytz.tzfile.Asia/Tokyo'>"

    zone = Tz.uk_tz()
    assert str(type(zone)) == "<class 'pytz.tzfile.Europe/London'>"

    zone = Tz.eastus_tz()
    assert str(type(zone)) == "<class 'pytz.tzfile.America/New_York'>"

    zone = Tz.westus_tz()
    assert str(type(zone)) == "<class 'pytz.tzfile.America/Los_Angeles'>"

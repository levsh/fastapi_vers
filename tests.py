import pytest
from unittest import mock

import fastapi_vers
from fastapi_vers import API, Version, VersionRange, merge_dicts


def test_merge_dicts():
    src = {}
    dst = {}
    dct = merge_dicts(src, dst)
    assert dct == {}

    src = {"a": "a"}
    dst = {}
    dct = merge_dicts(src, dst)
    assert dct == {"a": "a"}

    src = {}
    dst = {"a": "a"}
    dct = merge_dicts(src, dst)
    assert dct == {"a": "a"}

    src = {"a": "b"}
    dst = {"a": "a"}
    dct = merge_dicts(src, dst)
    assert dct == {"a": "b"}

    src = {"a": "a"}
    dst = {"b": "b"}
    dct = merge_dicts(src, dst)
    assert dct == {"a": "a", "b": "b"}

    src = {"a": {}}
    dst = {"a": {"aa": "aa"}}
    dct = merge_dicts(src, dst)
    assert dct == {"a": {"aa": "aa"}}

    src = {"a": {"aa": "aa"}}
    dst = {"a": {"aaa": "aaa"}, "b": ["b"]}
    dct = merge_dicts(src, dst)
    assert dct == {"a": {"aa": "aa", "aaa": "aaa"}, "b": ["b"]}

    src = {"a": ["a"]}
    dst = {"a": ["b"]}
    dct = merge_dicts(src, dst)
    assert dct == {"a": ["a"]}


def test_VersionRange():
    ver_range = VersionRange("0.0-0.9")
    assert ver_range.ver_from == Version("0.0")
    assert ver_range.ver_to == Version("0.9")
    assert str(ver_range) == "VersionRange(0.0-0.9)"
    assert repr(ver_range) == "VersionRange(0.0-0.9)"
    assert [ver for ver in ver_range] == [Version(f"0.{i}") for i in range(10)]

    with pytest.raises(ValueError):
        VersionRange("0.0.0-0.1.0")

    with pytest.raises(ValueError):
        VersionRange("0.0.a-0.1.0")

    with pytest.raises(ValueError):
        VersionRange("0.0-1.0")

    with pytest.raises(ValueError):
        VersionRange("1.0-0.0")

    with pytest.raises(ValueError):
        VersionRange(" 0.0 - 0.9 ")

    ver_range_a = VersionRange("0.1-0.2")
    ver_range_b = VersionRange("0.1-0.2")
    assert ver_range_a == ver_range_b


def test_API():
    api = API("0.5")
    assert api._latest == Version("0.5")
    assert api._app_kwds == {}
    assert api._app
    assert api.app == api._app

    api = API(
        "1.5",
        app_kwds={
            "all": {"version": "0.0.0"},
            "0.1": {"version": "0.1"},
        },
    )
    assert api._app_kwds == {
        "all": {"version": "0.0.0"},
        "0.1": {"version": "0.1"},
    }

    @api.version(["0.0-0.3", "1.0-latest"])
    def foo():
        pass

    assert foo.api_versions == [VersionRange("0.0-0.3"), VersionRange("1.0-1.5")]

    with pytest.raises(ValueError):

        @api.version(["0.0-0.3", "0.2-0.5"])
        def foo():
            pass

    with mock.patch.object(fastapi_vers.FastAPI, "__init__") as mock_call:
        mock_call.return_value = None
        api._make_ver_app(Version("0.0"))
        mock_call.assert_called_once_with(version="0.0.0")

    with mock.patch.object(fastapi_vers.FastAPI, "__init__") as mock_call:
        mock_call.return_value = None
        api._make_ver_app(Version("0.1"))
        mock_call.assert_called_once_with(version="0.1")

    @api.app.get("/")
    @api.version(["0.1-0.3"])
    async def root():
        pass

    api.get_versioned_app()

    with pytest.raises(ValueError):

        @api.app.get("/")
        @api.version(["1.1-1.9"])
        async def invalid():
            pass

        api.get_versioned_app()

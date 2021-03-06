from unittest import mock

import fastapi_vers
import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
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
            "default": {"version": "0.0.0"},
            "0.1": {"version": "0.1"},
        },
    )
    assert api._app_kwds == {
        "default": {"version": "0.0.0"},
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
        mock_call.assert_called_once()
        assert mock_call.call_args_list[0].kwargs["version"] == "0.0.0"

    with mock.patch.object(fastapi_vers.FastAPI, "__init__") as mock_call:
        mock_call.return_value = None
        api._make_ver_app(Version("0.1"))
        mock_call.assert_called_once()
        assert mock_call.call_args_list[0].kwargs["version"] == "0.1"

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


def test_x():
    api = API("0.3")

    @api.app.get("/")
    def root():
        pass

    @api.app.get("/foo")
    @api.version(["0.1-latest"])
    def foo():
        pass

    @api.app.get("/bar")
    @api.version(["0.1-0.2"])
    def bar():
        pass

    app = api.get_versioned_app()
    client = TestClient(app)

    assert client.get("/latest/").status_code == 200

    assert client.get("/0.1/foo").status_code == 200
    assert client.get("/0.2/foo").status_code == 200
    assert client.get("/0.3/foo").status_code == 200
    assert client.get("/latest/foo").status_code == 200

    assert client.get("/0.1/bar").status_code == 200
    assert client.get("/0.2/bar").status_code == 200
    assert client.get("/0.3/bar").status_code == 404
    assert client.get("/latest/bar").status_code == 404


def test_y():
    api = API("0.9")

    @api.app.get("/")
    @api.version(["0.2-0.3", "0.5-0.6"])
    def root():
        pass

    assert api.min_ver == Version("0.2")
    assert api.max_ver == Version("0.6")
    assert api.latest == Version("0.9")


def test_exception():
    api = API("0.1")

    @api.app.get("/test")
    @api.version(["0.1-latest"])
    def test():
        raise KeyError("x")

    @api.app.exception_handler(KeyError)
    def handler(request, exc):
        return JSONResponse(status_code=404, content=str(exc))

    app = api.get_versioned_app()
    client = TestClient(app)

    assert client.get("/latest/test").status_code == 404

    root_app = FastAPI()
    root_app.mount("/app", app)
    client = TestClient(root_app)

    assert client.get("/app/latest/test").status_code == 404

# fastapi_vers
API versioning concept for FastAPI

![tests](https://github.com/levsh/fastapi_vers/workflows/tests/badge.svg)

```bash
pip install fastapi_vers
```

```python
from fastapi import FastAPI
from fastapi_vers import API


api = API(
    "0.3",
    app_kwds={
        "all": {"title": "Versioned API", "version": "0.0"},
        "0.1": {"version": "0.1"},
        "0.2": {"version": "0.2"},
    }
)


@api.app.get("/")
async def root():
    return "Hello World!"


@api.app.get("/foo")
@api.version(["0.1-0.2"])
async def foo():
    return "This endpoint available only for 0.1, 0.2 api versions"


@api.app.get("/bar")
@api.version(["0.1-latest"])
async def bar():
    return "This endpoint available for 0.1, 0.2, 0.3 api versions"


app = FastAPI()
app.mount("/api", api.get_versioned_app())

"""
http://localhost:8000/api/latest

http://localhost:8000/api/0.1/foo
http://localhost:8000/api/0.2/foo

http://localhost:8000/api/0.1/bar
http://localhost:8000/api/0.2/bar
http://localhost:8000/api/0.3/bar
"""
```

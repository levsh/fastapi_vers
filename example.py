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
@api.version(["0.1-latest"])
async def root():
    return "Hello World!"


@api.app.get("/deprecated")
@api.version(["0.1-0.2"])
async def deprecated():
    return "This endpoint available only for 0.1, 0.2 api versions"


app = FastAPI()
app.mount("/api", api.get_versioned_app())

"""
http://localhost:8000/0.1
http://localhost:8000/0.2
http://localhost:8000/0.3
http://localhost:8000/latest


http://localhost:8000/0.1/deprecated
http://localhost:8000/0.2/deprecated
"""

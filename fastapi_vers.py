import copy
import re
from typing import Dict, List

from fastapi import FastAPI
from packaging.version import Version


__version__ = "0.1.1"


def merge_dicts(src: dict, dst: dict) -> dict:
    for k, v in src.items():
        if dst.get(k) is not None and isinstance(v, dict):
            merge_dicts(src[k], dst[k])
        else:
            dst[k] = v
    return dst


class VersionRange:
    regex = re.compile(r"^(?P<ver_from>\d+\.\d+)-(?P<ver_to>\d+\.\d+)$")

    def __init__(self, ver_range: str):
        match = self.regex.match(ver_range)
        if not match:
            raise ValueError("Version range value should match format X.X-X.X")
        groupdict = match.groupdict()
        ver_from = Version(groupdict["ver_from"])
        ver_to = Version(groupdict["ver_to"])
        if ver_to < ver_from:
            raise ValueError("Version from < Version to")
        if ver_from.major != ver_to.major:
            raise ValueError("Major componets mismatch")
        self.ver_from = ver_from
        self.ver_to = ver_to

    def __str__(self):
        return f"{self.__class__.__name__}({self.ver_from}-{self.ver_to})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.ver_from == other.ver_from and self.ver_to == other.ver_to

    def __iter__(self):
        major = self.ver_from.major
        return iter((Version(f"{major}.{minor}") for minor in range(self.ver_from.minor, self.ver_to.minor + 1)))


class API:
    def __init__(self, latest: str, app_kwds: Dict[str, dict] = None):
        self._latest = Version(latest)
        self._app_kwds = app_kwds or {}
        self._app = FastAPI()
        self._min_ver = None
        self._max_ver = None

    @property
    def app(self):
        return self._app

    @property
    def min_ver(self):
        return self._min_ver

    @property
    def max_ver(self):
        return self._max_ver

    @property
    def latest(self):
        return self._latest

    def version(self, ver_ranges: List[str]):
        api_versions = [
            VersionRange(re.sub(r"^(\d\.\d)-(latest)$", fr"\1-{self._latest}", ver_range)) for ver_range in ver_ranges
        ]

        s = set()
        for ver_range in api_versions:
            ss = set(str(ver) for ver in ver_range)
            if s.intersection(ss):
                raise ValueError("Versions intersection")
            s.update(ss)

        for ver_range in api_versions:
            self._min_ver = min(self._min_ver, ver_range.ver_from) if self._min_ver is not None else ver_range.ver_from
            self._max_ver = max(self._max_ver, ver_range.ver_to) if self._max_ver is not None else ver_range.ver_to

        def decorator(fn):
            fn.api_versions = api_versions
            return fn

        return decorator

    def get_versioned_app(self, **fastapi_kwds):
        latest = self._latest
        app = FastAPI(**fastapi_kwds)
        latest_app = self._make_ver_app(latest)
        apps = {latest: latest_app}
        for route in self.app.routes:
            ver_ranges = getattr(route.endpoint, "api_versions", None)
            if not ver_ranges:
                apps[latest].routes.append(route)
            else:
                for ver_range in ver_ranges:
                    for ver in ver_range:
                        if ver > latest:
                            raise ValueError(f"Version {ver} > latest")
                        if ver not in apps:
                            ver_app = self._make_ver_app(ver)
                            apps[ver] = ver_app
                        apps[ver].routes.append(route)
        for ver, ver_app in apps.items():
            app.mount("/" + str(ver), ver_app)
            if ver == latest:
                app.mount("/" + "latest", ver_app)
        return app

    def _make_ver_app(self, ver: Version):
        app_kwds = self._app_kwds.get(str(ver), {})
        if "default" in self._app_kwds:
            default_kwds = copy.deepcopy(self._app_kwds["default"])
            app_kwds = merge_dicts(app_kwds, default_kwds)
        return FastAPI(**app_kwds)

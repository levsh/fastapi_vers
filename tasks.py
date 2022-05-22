import os
import re

from invoke import task

CWD = os.path.abspath(os.path.dirname(__file__))


@task
def bump_major(c):
    regex = re.compile(r'.*__version__ = "(?P<major>\d+)\.(?P<minor>\d+)(\.\d+)?.*"', re.MULTILINE | re.DOTALL)
    filepath = os.path.abspath(os.path.join(CWD, "fastapi_vers.py"))
    with open(filepath, "r+") as f:
        text = f.read()
        match = regex.match(text)
        if match:
            groupdict = match.groupdict()
            major = int(groupdict["major"])
            text = re.sub(r'(.*__version__ = ")(\d+)\.(\d+)(\.\d+)?(".*)', fr"\g<1>{major+1}.0.0\g<5>", text)
            f.seek(0)
            f.write(text)
            f.truncate()


@task
def bump_minor(c):
    regex = re.compile(r'.*__version__ = "(?P<major>\d+)\.(?P<minor>\d+)(\.\d+)?.*"', re.MULTILINE | re.DOTALL)
    filepath = os.path.abspath(os.path.join(CWD, "fastapi_vers.py"))
    with open(filepath, "r+") as f:
        text = f.read()
        match = regex.match(text)
        if match:
            groupdict = match.groupdict()
            major = int(groupdict["major"])
            minor = int(groupdict["minor"])
            text = re.sub(r'(.*__version__ = ")(\d+)\.(\d+)(\.\d+)?(".*)', fr"\g<1>{major}.{minor+1}.0\g<5>", text)
            f.seek(0)
            f.write(text)
            f.truncate()


@task
def bump_dev(c):
    regex = re.compile(r'.*__version__ = "(?P<major>\d+)\.(?P<minor>\d+)(\.(?P<dev>\d+))?.*"', re.MULTILINE | re.DOTALL)
    filepath = os.path.abspath(os.path.join(CWD, "fastapi_vers.py"))
    with open(filepath, "r+") as f:
        text = f.read()
        match = regex.match(text)
        if match:
            groupdict = match.groupdict()
            major = int(groupdict["major"])
            minor = int(groupdict["minor"])
            dev = int(groupdict["dev"] or 0)
            text = re.sub(r'(.*__version__ = ")(\d+)\.(\d+)(\.\d+)?(".*)', fr"\g<1>{major}.{minor}.{dev+1}\g<5>", text)
            f.seek(0)
            f.write(text)
            f.truncate()


@task
def run_linter(c):
    cmd = "pipenv run flake8 --filename=*.py --count --show-source --statistics"
    c.run(cmd)


@task
def run_tests(c):
    cmd = "pipenv run coverage run --source fastapi_vers -m pytest tests.py && pipenv run coverage report -m"
    c.run(cmd)

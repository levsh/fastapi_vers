#!/bin/bash
pipenv run coverage run --source fastapi_vers -m pytest tests.py && pipenv run coverage report -m


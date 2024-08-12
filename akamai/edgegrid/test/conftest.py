# pylint: disable=missing-function-docstring
"""Unit tests helpers"""

import json
import os
import pytest

test_dir = os.path.abspath(os.path.dirname(__file__))


def cases():
    with open(f'{test_dir}/testcases.json', encoding="utf-8") as data:
        data = json.load(data)
    return data


@pytest.fixture(scope="package")
def testdata():
    with open(f'{test_dir}/testdata.json', encoding="utf-8") as data:
        data = json.load(data)
    return data


def names(tests):
    result = []
    for test in tests:
        result.append(test["testName"])
    return result


@pytest.fixture
def multipart_fields():
    with open(f'{test_dir}/sample_file.txt', "rb") as f:
        result = {
            "foo": "bar",
            "baz": ("sample_file.txt", f),
        }
        yield result


@pytest.fixture
def sample_file():
    with open(f'{test_dir}/sample_file.txt', "rb") as f:
        yield f

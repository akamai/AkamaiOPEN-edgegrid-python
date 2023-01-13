# pylint: disable=missing-function-docstring
"""unit tests for edgegrid. It runs tests from testcases.json"""

# Original author: Jonathan Landis <jlandis@akamai.com>
# Package maintainer: Akamai Developer Experience team <dl-devexp-eng@akamai.com>
#
# For more information visit https://developer.akamai.com

# Copyright 2021 Akamai Technologies, Inc. All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import re
import sys
import requests
import requests_toolbelt
import pytest

import akamai.edgegrid.edgegrid as eg
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from akamai.edgegrid.test.conftest import cases, names, test_dir

PY_VER = sys.version_info[0]
if sys.version_info[0] == 3:
    # python3
    from urllib.parse import urljoin
else:
    # python2.7
    from urlparse import urljoin

logger = logging.getLogger(__name__)

EXPECTED_CLIENT_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx='


def test_edge_grid_auth_headers(testdata):
    auth_headers = eg.EdgeGridAuthHeaders(
        client_token=testdata['client_token'],
        client_secret=testdata['client_secret'],
        access_token=testdata['access_token'],
        headers_to_sign=testdata['headers_to_sign'],
        max_body=testdata['max_body']
    )

    sign_key = auth_headers.make_signing_key(testdata['timestamp'])
    assert sign_key == testdata["sign_key_test"]

    content_hash = auth_headers.make_content_hash(
        body="test_body",
        method="POST"
    )
    assert content_hash == testdata["content_hash_test"]

    header = auth_headers.get_header_versions()
    assert header == {}


@pytest.mark.parametrize("testcase", cases(), ids=names(cases()))
def test_edge_grid(testdata, testcase):
    auth = EdgeGridAuth(
        client_token=testdata['client_token'],
        client_secret=testdata['client_secret'],
        access_token=testdata['access_token'],
        headers_to_sign=testdata['headers_to_sign'],
        max_body=testdata['max_body']
    )

    headers = {}
    if 'headers' in testcase['request']:
        for request_headers in testcase['request']['headers']:
            for key, val in request_headers.items():
                headers[key] = val

    req = requests.Request(
        method=testcase['request']['method'],
        url=urljoin(
            testdata['base_url'],
            testcase['request']['path']),
        headers=headers,
        data=testcase['request'].get('data')
    )

    if testcase.get('failsWithMessage') is None:
        req = req.prepare()
        data_to_sign = auth.ah.make_data_to_sign(req.url, req.headers, "", req.method, req.body)
        auth_header = auth.ah.make_auth_header(
            req.url, req.headers, req.method, req.body, testdata['timestamp'],
            testdata['nonce']
        )
        assert auth_header == testcase['expectedAuthorization']
        assert data_to_sign == testcase['expectedDataToSign']
    else:
        with pytest.raises(Exception) as exception:
            req = req.prepare()
            auth.ah.make_data_to_sign(req.url, req.headers, "", req.method, req.body)
            auth.ah.make_auth_header(
                req.url, req.headers, req.method, req.body, testdata['timestamp'],
                testdata['nonce']
            )
            logger.debug('Got exception from make_auth_header', exc_info=True)
            assert str(exception) == testcase['failsWithMessage']


def test_nonce():
    count = 100
    nonces = set()
    while count > 0:
        nonce = eg.new_nonce()
        assert nonce not in nonces
        count -= 1


def test_timestamp():
    valid_timestamp = re.compile(r"""
    ^
        \d{4} # year
        [0-1][0-9] # month
        [0-3][0-9] # day
        T
        [0-2][0-9] # hour
        :
        [0-5][0-9] # minute
        :
        [0-5][0-9] # second
        \+0000 # timezone
    $
    """, re.VERBOSE)
    assert re.match(valid_timestamp, eg.eg_timestamp())


def test_defaults():
    auth = EdgeGridAuth(
        client_token='xxx', client_secret='xxx', access_token='xxx'
    )
    assert auth.ah.max_body == 131072
    assert auth.ah.headers_to_sign == []


def test_edgerc_default():
    auth = EdgeGridAuth.from_edgerc(os.path.join(test_dir, 'sample_edgerc'))
    assert auth.ah.client_token == 'xxxx-xxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx'
    assert auth.ah.client_secret == EXPECTED_CLIENT_SECRET
    assert auth.ah.access_token == 'xxxx-xxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx'
    assert auth.ah.max_body == 131072
    assert auth.ah.headers_to_sign == ['none']


def test_edgerc_broken():
    auth = EdgeGridAuth.from_edgerc(
        os.path.join(test_dir, 'sample_edgerc'), 'broken')
    assert auth.ah.client_secret == EXPECTED_CLIENT_SECRET
    assert auth.ah.access_token == 'xxxx-xxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx'
    assert auth.ah.max_body == 128 * 1024
    assert auth.ah.headers_to_sign == ['none']


def test_edgerc_unparseable():
    with pytest.raises(BaseException):
        EdgeGridAuth.from_edgerc(
            os.path.join(test_dir, 'edgerc_that_doesnt_parse'))


def test_edgerc_headers():
    auth = EdgeGridAuth.from_edgerc(
        os.path.join(test_dir, 'sample_edgerc'), 'headers')
    assert auth.ah.headers_to_sign == ['x-mything1', 'x-mything2']


def test_get_header_versions():
    auth = EdgeGridAuth.from_edgerc(
        os.path.join(test_dir, 'sample_edgerc'), 'headers')
    header = auth.ah.get_header_versions()
    assert 'user-agent' not in header

    header = auth.ah.get_header_versions({'User-Agent': 'testvalue'})
    assert 'User-Agent' in header

    # setting environment variables with hardcoded `1.0.0` value, just for this test.
    # These variables are cleared at the end of this test.
    os.environ["AKAMAI_CLI"] = '1.0.0'
    os.environ["AKAMAI_CLI_VERSION"] = '1.0.0'

    header = auth.ah.get_header_versions()
    assert 'User-Agent' in header
    assert header['User-Agent'] == 'AkamaiCLI/1.0.0'

    header = auth.ah.get_header_versions({'User-Agent': 'test-agent'})
    assert 'User-Agent' in header
    assert header['User-Agent'] == 'test-agent AkamaiCLI/1.0.0'

    os.environ["AKAMAI_CLI_COMMAND"] = '1.0.0'
    os.environ["AKAMAI_CLI_COMMAND_VERSION"] = '1.0.0'

    header = auth.ah.get_header_versions()
    assert 'User-Agent' in header
    assert header['User-Agent'] == 'AkamaiCLI/1.0.0 AkamaiCLI-1.0.0/1.0.0'

    header = auth.ah.get_header_versions({'User-Agent': 'testvalue'})
    assert 'User-Agent' in header
    assert header['User-Agent'] == 'testvalue AkamaiCLI/1.0.0 AkamaiCLI-1.0.0/1.0.0'

    del os.environ['AKAMAI_CLI']
    del os.environ['AKAMAI_CLI_VERSION']
    del os.environ['AKAMAI_CLI_COMMAND']
    del os.environ['AKAMAI_CLI_COMMAND_VERSION']

    assert 'AKAMAI_CLI' not in os.environ
    assert 'AKAMAI_CLI_VERSION' not in os.environ
    assert 'AKAMAI_CLI_COMMAND' not in os.environ
    assert 'AKAMAI_CLI_COMMAND_VERSION' not in os.environ


def test_edgerc_from_object():
    auth = EdgeGridAuth.from_edgerc(
        EdgeRc(os.path.join(test_dir, 'sample_edgerc')))
    assert auth.ah.client_token == 'xxxx-xxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx'
    assert auth.ah.client_secret == EXPECTED_CLIENT_SECRET
    assert auth.ah.access_token == 'xxxx-xxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx'
    assert auth.ah.max_body == 131072
    assert auth.ah.headers_to_sign == ['none']


def test_edgerc_dashes():
    auth = EdgeGridAuth.from_edgerc(
        os.path.join(test_dir, 'sample_edgerc'), 'dashes')
    assert auth.ah.max_body == 128 * 1024


def test_get_multipart_body():
    with open(f'{test_dir}/sample_file.txt', "rb") as sample_file:
        encoder = requests_toolbelt.MultipartEncoder(
            fields={
                "foo": "bar",
                "baz": ("sample_file.txt", sample_file),
            },
            boundary="multipart_boundary",
        )
        assert eg.get_multipart_body(encoder, size=20) == b"--multipart_boundary"
        assert eg.get_multipart_body(encoder) == encoder.to_string()


def test_json(testdata):
    auth = EdgeGridAuth(
        client_token=testdata['client_token'],
        client_secret=testdata['client_secret'],
        access_token=testdata['access_token'],
    )

    params = {
        'extended': 'true',
    }

    data = {
        'key': 'value',
    }

    request = requests.Request(
        method='POST',
        url=urljoin(testdata['base_url'], '/testapi/v1/t3'),
        params=params,
        json=data,
    )

    req = request.prepare()
    auth_header = auth.ah.make_auth_header(
        req.url, req.headers, req.method, req.body, testdata['timestamp'],
        testdata['nonce']
    )

    assert auth_header == testdata['jsontest_hash']


def test_multipart_encoder(testdata, multipart_fields):
    auth = EdgeGridAuth(
        client_token=testdata["client_token"],
        client_secret=testdata["client_secret"],
        access_token=testdata["access_token"],
    )

    params = {
        "extended": "true",
    }

    data = requests_toolbelt.MultipartEncoder(
        fields=multipart_fields,
        boundary="multipart_boundary",
    )

    request = requests.Request(
        method="POST",
        url=urljoin(testdata["base_url"], "/testapi/v1/t3"),
        params=params,
        data=data,
    )

    req = request.prepare()
    auth_header = auth.ah.make_auth_header(
        req.url, req.headers, req.method, req.body, testdata["timestamp"], testdata["nonce"]
    )

    # close any open files
    for part_value in multipart_fields.values():
        file = part_value[1] if isinstance(part_value, (list, tuple)) else part_value
        try:
            file.close()
        except AttributeError:
            pass

    assert auth_header == testdata["multipart_hash_test"]

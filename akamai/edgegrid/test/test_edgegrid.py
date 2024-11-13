# pylint: disable=missing-function-docstring
"""unit tests for edgegrid. It runs tests from testcases.json"""

import io
import logging
import os
import re
import unittest.mock
from urllib.parse import urljoin

import requests
import requests_toolbelt
import pytest

import akamai.edgegrid.edgegrid as eg
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from akamai.edgegrid.test.conftest import cases, names, test_dir

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


def test_make_content_hash_logs_warning_for_unknown_body_len(testdata, caplog):
    auth_headers = eg.EdgeGridAuthHeaders(
        client_token=testdata['client_token'],
        client_secret=testdata['client_secret'],
        access_token=testdata['access_token'],
        headers_to_sign=testdata['headers_to_sign'],
        max_body=testdata['max_body']
    )

    def throwing_determine_body_len(_):
        raise OSError('boom')

    with unittest.mock.patch('akamai.edgegrid.edgegrid.determine_body_len',
                             throwing_determine_body_len):
        content_hash = auth_headers.make_content_hash(body="test_body", method="POST")
        assert content_hash == testdata["content_hash_test"]
        assert re.match(r'WARNING.+cannot determine length of request body=.+:\s+boom',
                        caplog.text)


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

    # The auth plugin is called on a PreparedRequest object, not a Request (see
    # PreparedRequest.prepare()). That's why we want req to be a PreparedRequest
    # in order to test make_auth_header with proper data.
    if testcase.get('failsWithMessage') is None:
        req = req.prepare()
        data_to_sign = auth.ah.make_data_to_sign(req, "")
        auth_header = auth.ah.make_auth_header(req, testdata['timestamp'], testdata['nonce'])
        assert auth_header == testcase['expectedAuthorization']
        assert data_to_sign == testcase['expectedDataToSign']
    else:
        with pytest.raises(Exception) as exc_info:
            req.prepare()
        assert str(exc_info.value) == testcase['failsWithMessage']


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


class TestReadBodyContent:
    """Test read_body_content"""
    def test_reading_from_str(self):
        assert eg.read_body_content('foobar', 10) == b'foobar'

    def test_reading_from_str_truncated(self):
        assert eg.read_body_content('foobar', 3) == b'foo'

    def test_reading_from_bytes(self):
        assert eg.read_body_content(b'foobar', 10) == b'foobar'

    def test_reading_from_bytes_truncated(self):
        assert eg.read_body_content(b'foobar', 3) == b'foo'

    def test_basic_reading_from_file_object(self, sample_file):
        assert eg.read_body_content(sample_file, 32) == b'this is a sample file.'

    def test_basic_reading_from_multipart_encoder(self):
        def encoder():
            return requests_toolbelt.MultipartEncoder({'foo': 'bar'}, boundary='baz')

        assert eg.read_body_content(encoder(), 1024) == encoder().to_string()


class TestReadStreamAndRewind:
    """Test read_stream_and_rewind"""
    def test_with_file_object(self, sample_file):
        assert eg.read_stream_and_rewind(sample_file, 32) == b'this is a sample file.'
        assert sample_file.read() == b'this is a sample file.'

    def test_with_file_object_truncated(self, sample_file):
        assert eg.read_stream_and_rewind(sample_file, 4) == b'this'
        assert sample_file.read() == b'this is a sample file.'

    def test_with_multipart_encoder(self, multipart_fields):
        encoder = requests_toolbelt.MultipartEncoder(multipart_fields, "multipart_boundary")

        buf = eg.read_stream_and_rewind(encoder, 1024)
        assert buf == encoder.to_string()
        assert buf.startswith(b'--multipart_boundary')
        assert len(buf) == encoder.len

    def test_with_multipart_encoder_truncated(self, multipart_fields):
        encoder = requests_toolbelt.MultipartEncoder(multipart_fields, "multipart_boundary")

        assert eg.read_stream_and_rewind(encoder, 20) == b'--multipart_boundary'
        buf = eg.read_stream_and_rewind(encoder, 1024)
        assert buf == encoder.to_string()
        assert buf.startswith(b'--multipart_boundary')
        assert len(buf) == encoder.len

    def test_raises_when_input_has_no_read_method(self):
        with pytest.raises(TypeError) as excinfo:
            eg.read_stream_and_rewind('foo', 10)
        assert excinfo.match('akamai.edgegrid: unexpected body type: str')
        assert str(excinfo.value.__cause__) == "'str' object has no attribute 'read'"

    def test_raises_when_input_has_no_seek_method(self):
        # pylint: disable=missing-class-docstring,too-few-public-methods
        class DummyReader:
            def read(self, _):
                return b'Hello'

        with pytest.raises(TypeError) as excinfo:
            eg.read_stream_and_rewind(DummyReader(), 10)
        assert excinfo.match('akamai.edgegrid: unexpected body type: DummyReader')
        assert str(excinfo.value.__cause__) == "'DummyReader' object has no attribute '_buffer'"

    def test_raises_when_stream_not_seekable(self):
        r, w = os.pipe()
        os.write(w, b'Hello, pipe!')
        os.close(w)
        with pytest.raises(io.UnsupportedOperation) as excinfo:
            with open(r, 'rb') as pipe:
                eg.read_stream_and_rewind(pipe, 10)
        assert excinfo.match('not seekable')


class TestDetermineBodyLen:
    """Test determine_body_len"""
    def test_with_str(self):
        assert eg.determine_body_len('foobarbaz') == 9

    def test_with_bytes(self):
        assert eg.determine_body_len(b'foobarbaz') == 9

    def test_with_file(self, sample_file):
        assert eg.determine_body_len(sample_file) == len('this is a sample file.')

    def test_with_multipart_encoder(self, multipart_fields):
        encoder = requests_toolbelt.MultipartEncoder(multipart_fields, "boundary")
        assert eg.determine_body_len(encoder) == encoder.len

    def test_raises_on_unknown_body_type(self):
        with pytest.raises(TypeError) as excinfo:
            eg.determine_body_len({'foo': 'bar'})
        assert excinfo.match('akamai.edgegrid: unexpected body type: dict')
        assert str(excinfo.value.__cause__) == "'dict' object has no attribute 'fileno'"

    def test_raises_when_filelike_body_does_not_support_file_descriptors(self):
        with pytest.raises(io.UnsupportedOperation) as excinfo:
            eg.determine_body_len(io.StringIO("Hello, string"))
        assert excinfo.match('fileno')


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
    auth_header = auth.ah.make_auth_header(req, testdata['timestamp'], testdata['nonce'])

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
    auth_header = auth.ah.make_auth_header(req, testdata["timestamp"], testdata["nonce"])

    assert auth_header == testdata["multipart_hash_test"]

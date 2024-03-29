#
# unit tests for edgegrid. runs tests from testdata.json
#
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

import akamai.edgegrid.edgegrid as eg
from akamai.edgegrid import EdgeGridAuth, EdgeRc
import json
import logging
import os
import re
import requests
import requests_toolbelt
import sys
import unittest

PY_VER = sys.version_info[0]
if sys.version_info[0] == 3:
    # python3
    from urllib.parse import urljoin
else:
    # python2.7
    from urlparse import urljoin


mydir = os.path.abspath(os.path.dirname(__file__))
logger = logging.getLogger(__name__)

expected_client_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx='


class EdgeGridAuthHeadersTest(unittest.TestCase):
    def __init__(self, testdata=None, testcase=None):
        super(EdgeGridAuthHeadersTest, self).__init__()
        self.testdata = testdata
        self.testcase = testcase
        self.maxDiff = None

    def runTest(self):
        self.ah = eg.EdgeGridAuthHeaders(
            client_token=self.testdata['client_token'],
            client_secret=self.testdata['client_secret'],
            access_token=self.testdata['access_token'],
            headers_to_sign=self.testdata['headers_to_sign'],
            max_body=self.testdata['max_body']
        )

        sign_key = self.ah.make_signing_key(self.testdata['timestamp'])
        self.assertEqual(sign_key, self.testdata["sign_key_test"])

        content_hash = self.ah.make_content_hash(
            body="test_body",
            method="POST"
        )
        self.assertEqual(content_hash, self.testdata["content_hash_test"])

        header = self.ah.get_header_versions()
        self.assertEqual(header, {})


class EdgeGridTest(unittest.TestCase):
    def __init__(self, testdata=None, testcase=None):
        super(EdgeGridTest, self).__init__()
        self.testdata = testdata
        self.testcase = testcase
        self.maxDiff = None

    def runTest(self):
        auth = EdgeGridAuth(
            client_token=self.testdata['client_token'],
            client_secret=self.testdata['client_secret'],
            access_token=self.testdata['access_token'],
            headers_to_sign=self.testdata['headers_to_sign'],
            max_body=self.testdata['max_body']
        )

        headers = {}
        if 'headers' in self.testcase['request']:
            for h in self.testcase['request']['headers']:
                for k, v in h.items():
                    headers[k] = v

        request = requests.Request(
            method=self.testcase['request']['method'],
            url=urljoin(
                self.testdata['base_url'],
                self.testcase['request']['path']),
            headers=headers,
            data=self.testcase['request'].get('data') if self.testcase['request'].get('data')
            else None
        )

        try:
            r = request.prepare()
            data_to_sign = auth.ah.make_data_to_sign(r.url, r.headers, "", r.method, r.body)
            auth_header = auth.ah.make_auth_header(
                r.url, r.headers, r.method, r.body, self.testdata['timestamp'],
                self.testdata['nonce']
            )
        except Exception as e:
            logger.debug('Got exception from make_auth_header', exc_info=True)
            self.assertEqual(str(e), self.testcase['failsWithMessage'])
            return

        self.assertEqual(auth_header, self.testcase['expectedAuthorization'])
        self.assertEqual(data_to_sign, self.testcase['expectedDataToSign'])


class EGSimpleTest(unittest.TestCase):
    def test_nonce(self):
        count = 100
        nonces = set()
        while count > 0:
            n = eg.new_nonce()
            self.assertNotIn(n, nonces)
            count -= 1

    def test_timestamp(self):
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
        if PY_VER >= 3:
            self.assertRegex(eg.eg_timestamp(), valid_timestamp)
        else:
            self.assertRegexpMatches(eg.eg_timestamp(), valid_timestamp)

    def test_defaults(self):
        auth = EdgeGridAuth(
            client_token='xxx', client_secret='xxx', access_token='xxx'
        )
        self.assertEqual(auth.ah.max_body, 131072)
        self.assertEqual(auth.ah.headers_to_sign, [])

    def test_edgerc_default(self):
        auth = EdgeGridAuth.from_edgerc(os.path.join(mydir, 'sample_edgerc'))
        self.assertEqual(
            auth.ah.client_token,
            'xxxx-xxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx')
        self.assertEqual(
            auth.ah.client_secret,
            expected_client_secret)
        self.assertEqual(
            auth.ah.access_token,
            'xxxx-xxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx')
        self.assertEqual(auth.ah.max_body, 131072)
        self.assertEqual(auth.ah.headers_to_sign, ['none'])

    def test_edgerc_broken(self):
        auth = EdgeGridAuth.from_edgerc(
            os.path.join(mydir, 'sample_edgerc'), 'broken')
        self.assertEqual(
            auth.ah.client_secret,
            expected_client_secret)
        self.assertEqual(
            auth.ah.access_token,
            'xxxx-xxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx')
        self.assertEqual(auth.ah.max_body, 128 * 1024)
        self.assertEqual(auth.ah.headers_to_sign, ['none'])

    def test_edgerc_unparseable(self):
        # noinspection PyBroadException
        try:
            EdgeGridAuth.from_edgerc(
                os.path.join(mydir, 'edgerc_that_doesnt_parse'))
            self.fail("should have thrown an exception")
        except BaseException:
            pass

    def test_edgerc_headers(self):
        auth = EdgeGridAuth.from_edgerc(
            os.path.join(mydir, 'sample_edgerc'), 'headers')
        self.assertEqual(auth.ah.headers_to_sign, ['x-mything1', 'x-mything2'])

    def test_get_header_versions(self):
        auth = EdgeGridAuth.from_edgerc(
            os.path.join(mydir, 'sample_edgerc'), 'headers')
        header = auth.ah.get_header_versions()
        self.assertFalse('user-agent' in header)

        header = auth.ah.get_header_versions({'User-Agent': 'testvalue'})
        self.assertTrue('User-Agent' in header)

        # setting environment variables with hardcoded `1.0.0` value, just for this test.
        # These variables are cleared at the end of this test.
        os.environ["AKAMAI_CLI"] = '1.0.0'
        os.environ["AKAMAI_CLI_VERSION"] = '1.0.0'

        header = auth.ah.get_header_versions()
        self.assertTrue('User-Agent' in header)
        self.assertEqual(header['User-Agent'], 'AkamaiCLI/1.0.0')

        header = auth.ah.get_header_versions({'User-Agent': 'test-agent'})
        self.assertTrue('User-Agent' in header)
        self.assertEqual(header['User-Agent'], 'test-agent AkamaiCLI/1.0.0')

        os.environ["AKAMAI_CLI_COMMAND"] = '1.0.0'
        os.environ["AKAMAI_CLI_COMMAND_VERSION"] = '1.0.0'

        header = auth.ah.get_header_versions()
        self.assertTrue('User-Agent' in header)
        self.assertEqual(header['User-Agent'],
                         'AkamaiCLI/1.0.0 AkamaiCLI-1.0.0/1.0.0')

        header = auth.ah.get_header_versions({'User-Agent': 'testvalue'})
        self.assertTrue('User-Agent' in header)
        self.assertEqual(
            header['User-Agent'],
            'testvalue AkamaiCLI/1.0.0 AkamaiCLI-1.0.0/1.0.0')

        del os.environ['AKAMAI_CLI']
        del os.environ['AKAMAI_CLI_VERSION']
        del os.environ['AKAMAI_CLI_COMMAND']
        del os.environ['AKAMAI_CLI_COMMAND_VERSION']

        self.assertFalse('AKAMAI_CLI' in os.environ)
        self.assertFalse('AKAMAI_CLI_VERSION' in os.environ)
        self.assertFalse('AKAMAI_CLI_COMMAND' in os.environ)
        self.assertFalse('AKAMAI_CLI_COMMAND_VERSION' in os.environ)

    def test_edgerc_from_object(self):
        auth = EdgeGridAuth.from_edgerc(
            EdgeRc(os.path.join(mydir, 'sample_edgerc')))
        self.assertEqual(
            auth.ah.client_token,
            'xxxx-xxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx')
        self.assertEqual(
            auth.ah.client_secret,
            expected_client_secret)
        self.assertEqual(
            auth.ah.access_token,
            'xxxx-xxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx')
        self.assertEqual(auth.ah.max_body, 131072)
        self.assertEqual(auth.ah.headers_to_sign, ['none'])

    def test_edgerc_dashes(self):
        auth = EdgeGridAuth.from_edgerc(
            os.path.join(mydir, 'sample_edgerc'), 'dashes')
        self.assertEqual(auth.ah.max_body, 128 * 1024)

    def test_get_multipart_body(self):
        with open("%s/sample_file.txt" % mydir, "rb") as sample_file:
            encoder = requests_toolbelt.MultipartEncoder(
                fields={
                    "foo": "bar",
                    "baz": ("sample_file.txt", sample_file),
                },
                boundary="multipart_boundary",
            )
            self.assertEqual(eg.get_multipart_body(encoder, size=20), b"--multipart_boundary")
            self.assertEqual(eg.get_multipart_body(encoder), encoder.to_string())


class JsonTest(unittest.TestCase):
    def __init__(self, testdata=None, testcase=None):
        super(JsonTest, self).__init__()
        self.testdata = testdata
        self.testcase = testcase
        self.maxDiff = None

    def runTest(self):
        auth = EdgeGridAuth(
            client_token=self.testdata['client_token'],
            client_secret=self.testdata['client_secret'],
            access_token=self.testdata['access_token'],
        )

        params = {
            'extended': 'true',
        }

        data = {
            'key': 'value',
        }

        request = requests.Request(
            method='POST',
            url=urljoin(self.testdata['base_url'], '/testapi/v1/t3'),
            params=params,
            json=data,
        )

        r = request.prepare()
        auth_header = auth.ah.make_auth_header(
            r.url, r.headers, r.method, r.body, self.testdata['timestamp'],
            self.testdata['nonce']
        )

        self.assertEqual(auth_header, self.testdata['jsontest_hash'])


class MultipartEncoderTest(unittest.TestCase):
    def __init__(self, testdata=None, multipart_fields=None):
        super(MultipartEncoderTest, self).__init__()
        self.testdata = testdata
        self.multipart_fields = multipart_fields
        self.maxDiff = None

    def runTest(self):
        auth = EdgeGridAuth(
            client_token=self.testdata["client_token"],
            client_secret=self.testdata["client_secret"],
            access_token=self.testdata["access_token"],
        )

        params = {
            "extended": "true",
        }

        data = requests_toolbelt.MultipartEncoder(
            fields=self.multipart_fields,
            boundary="multipart_boundary",
        )

        request = requests.Request(
            method="POST",
            url=urljoin(self.testdata["base_url"], "/testapi/v1/t3"),
            params=params,
            data=data,
        )

        r = request.prepare()
        auth_header = auth.ah.make_auth_header(
            r.url, r.headers, r.method, r.body, self.testdata["timestamp"], self.testdata["nonce"]
        )

        # close any open files
        for part_value in self.multipart_fields.values():
            f = part_value[1] if isinstance(part_value, (list, tuple)) else part_value
            try:
                f.close()
            except AttributeError:
                pass

        self.assertEqual(auth_header, self.testdata["multipart_hash_test"])


def suite():
    suite = unittest.TestSuite()
    with open("%s/testdata.json" % mydir) as testdata:
        testdata = json.load(testdata)

    tests = testdata['tests']
    del testdata['tests']

    for test in tests:
        suite.addTest(EdgeGridTest(testdata, test))
        suite.addTest(EdgeGridAuthHeadersTest(testdata, test))

    suite.addTest(JsonTest(testdata))

    sample_file = open("%s/sample_file.txt" % mydir, "rb")
    suite.addTest(
        MultipartEncoderTest(
            testdata,
            multipart_fields={
                "foo": "bar",
                "baz": ("sample_file.txt", sample_file),
            },
        )
    )

    suite.addTest(EGSimpleTest('test_nonce'))
    suite.addTest(EGSimpleTest('test_timestamp'))
    suite.addTest(EGSimpleTest('test_defaults'))
    suite.addTest(EGSimpleTest('test_edgerc_default'))
    suite.addTest(EGSimpleTest('test_edgerc_broken'))
    suite.addTest(EGSimpleTest('test_edgerc_unparseable'))
    suite.addTest(EGSimpleTest('test_edgerc_headers'))
    suite.addTest(EGSimpleTest('test_get_header_versions'))
    suite.addTest(EGSimpleTest('test_edgerc_from_object'))
    suite.addTest(EGSimpleTest('test_get_multipart_body'))

    return suite


def load_tests(loader=None, tests=None, pattern=None):
    return suite()


if __name__ == '__main__':
    runner = unittest.TextTestRunner().run(suite())

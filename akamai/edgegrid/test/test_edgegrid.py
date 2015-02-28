#
# unit tests for edgegrid. runs tests from testdata.json
#
# Original author: Jonathan Landis <jlandis@akamai.com>
#
# For more information visit https://developer.akamai.com

# Copyright 2014 Akamai Technologies, Inc. All Rights Reserved
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

import json
import logging
import os
import re
import requests
import sys
import traceback
import unittest

if sys.version_info[0] == 3:
    # python3
    from urllib.parse import urljoin
else:
    # python2.7
    from urlparse import urljoin

from akamai.edgegrid import EdgeGridAuth, EdgeRc
import akamai.edgegrid.edgegrid as eg

mydir=os.path.abspath(os.path.dirname(__file__))
logger = logging.getLogger(__name__)

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

        headers = { }
        if 'headers' in self.testcase['request']:
            for h in self.testcase['request']['headers']:
                for k,v in h.items():
                    headers[k] = v

        request = requests.Request(
            method=self.testcase['request']['method'],
            url=urljoin(self.testdata['base_url'],self.testcase['request']['path']),   
            headers=headers,
            data=self.testcase['request'].get('data') if self.testcase['request'].get('data') \
                                                      else None
        )

        try:
            auth_header = auth.make_auth_header(
                request.prepare(), self.testdata['timestamp'], self.testdata['nonce']
            )
        except Exception as e:
            logger.debug('Got exception from make_auth_header', exc_info=True)
            self.assertEquals(str(e), self.testcase['failsWithMessage'])
            return

        self.assertEqual(auth_header, self.testcase['expectedAuthorization'])

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
        self.assertRegexpMatches(eg.eg_timestamp(), valid_timestamp)

    def test_defaults(self):
        auth = EdgeGridAuth(
            client_token='xxx', client_secret='xxx', access_token='xxx'
        )
        self.assertEqual(auth.max_body, 2048)
        self.assertEqual(auth.headers_to_sign, [])

    def test_edgerc_default(self):
        auth = EdgeGridAuth.from_edgerc(os.path.join(mydir, 'sample_edgerc'))
        self.assertEqual(auth.client_token, 'xxxx-xxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx')
        self.assertEqual(auth.client_secret, 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=')
        self.assertEqual(auth.access_token, 'xxxx-xxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx')
        self.assertEqual(auth.max_body, 131072)
        self.assertEqual(auth.headers_to_sign, [])

    def test_edgerc_broken(self):
        auth = EdgeGridAuth.from_edgerc(os.path.join(mydir, 'sample_edgerc'), 'broken')
        self.assertEqual(auth.client_secret, 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=')
        self.assertEqual(auth.access_token, 'xxxx-xxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx')
        self.assertEqual(auth.max_body, 2048)
        self.assertEqual(auth.headers_to_sign, [])

    def test_edgerc_unparseable(self):
        try:
            auth = EdgeGridAuth.from_edgerc(os.path.join(mydir, 'edgerc_test_doesnt_parse'))
            self.fail("should have thrown an exception")
        except:
            pass

    def test_edgerc_headers(self):
        auth = EdgeGridAuth.from_edgerc(os.path.join(mydir, 'sample_edgerc'), 'headers')
        self.assertEqual(auth.headers_to_sign, ['x-mything1', 'x-mything2'])

    def test_edgerc_from_object(self):
        auth = EdgeGridAuth.from_edgerc(EdgeRc(os.path.join(mydir, 'sample_edgerc')))
        self.assertEqual(auth.client_token, 'xxxx-xxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx')
        self.assertEqual(auth.client_secret, 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=')
        self.assertEqual(auth.access_token, 'xxxx-xxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx')
        self.assertEqual(auth.max_body, 131072)
        self.assertEqual(auth.headers_to_sign, [])

def suite():
    suite = unittest.TestSuite()
    with open("%s/testdata.json" % mydir) as testdata:
        testdata = json.load(testdata)

    tests = testdata['tests']
    del testdata['tests']

    for test in tests:
        suite.addTest(EdgeGridTest(testdata, test))

    suite.addTest(EGSimpleTest('test_nonce'))
    suite.addTest(EGSimpleTest('test_timestamp'))
    suite.addTest(EGSimpleTest('test_defaults'))
    suite.addTest(EGSimpleTest('test_edgerc_default'))
    suite.addTest(EGSimpleTest('test_edgerc_broken'))
    suite.addTest(EGSimpleTest('test_edgerc_unparseable'))
    suite.addTest(EGSimpleTest('test_edgerc_headers'))
    suite.addTest(EGSimpleTest('test_edgerc_from_object'))

    return suite

def load_tests(loader=None, tests=None, pattern=None):
    return suite()

if __name__ == '__main__':
    runner = unittest.TextTestRunner().run(suite())


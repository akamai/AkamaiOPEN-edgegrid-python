#!/usr/bin/env python
#
# EdgeGrid requests Auth handler
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

import requests
import logging
import uuid
import hashlib
import hmac
import base64
import re
import sys
from requests.auth import AuthBase
from time import gmtime, strftime

if sys.version_info[0] == 3:
    from urllib.urlparse import urlparse, parse_qsl, urlunparse
else:
    from urlparse import urlparse, parse_qsl, urlunparse

#if sys.version_info[0] != 2 or sys.version_info[1] < 7:
#    print("This script requires Python version 2.7")
#    sys.exit(1)

logger = logging.getLogger(__name__)

__all__=['EdgeGridAuth']

def eg_timestamp():
    return strftime('%Y%m%dT%H:%M:%S+0000', gmtime())

def new_nonce():
    return uuid.uuid4()

def base64_hmac_sha256(data, key):
    return base64.b64encode(hmac.new(bytes(key), bytes(data), hashlib.sha256).digest())

def base64_sha256(data):
    return base64.b64encode(hashlib.sha256(data).digest())

class EdgeGridAuth(AuthBase):
    """A Requests authentication handler that provides Akamai {OPEN} EdgeGrid support.

    Basic Usage::
        >>> import requests
        >>> from akamai.edgegrid import EdgeGridAuth
        >>> s = requests.Session()
        >>> s.auth = EdgeGridAuth(
            client_token='cccccccccccccccccc',
            client_secret='sssssssssssssssss',
            access_token='aaaaaaaaaaaaaaaaa'
        )

    """

    def __init__(self, client_token, client_secret, access_token, 
                 headers_to_sign=None, max_body=2048, testurl=None):
        """Initialize authentication using the given parameters from the Luna Manage APIs
           Interface:

        :param client_token: Client token provided by "Credentials" ui
        :param client_secret: Client secret provided by "Credentials" ui
        :param access_token: Access token provided by "Authorizations" ui
        :param headers_to_sign: An ordered list header names that will be included in 
            the signature.  This will be provided by specific APIs. (default [])
        :param max_body: Maximum content body size for POST requests. This will be provided by
            specific APIs. (default 2048)
        :param testurl: Use this value for method and host portion of URL when signing.

        """
        self.client_token = client_token
        self.client_secret = client_secret
        self.access_token = access_token
        if headers_to_sign:
            self.headers_to_sign = [ h.lower() for h in headers_to_sign ]
        else:
            self.headers_to_sign = []
        self.max_body = max_body
        self.testurl = testurl

    def make_signing_key(self, timestamp):
        signing_key = base64_hmac_sha256(timestamp, self.client_secret)
        logger.debug('signing key: %s', signing_key)
        return signing_key

    def canonicalize_headers(self, r):
        spaces_re = re.compile('\\s+')

        # note: r.headers is a case-insensitive dict and self.headers_to_sign
        # should already be lowercased at this point
        return '\t'.join([
            "%s:%s" % (h, spaces_re.sub(' ', r.headers[h].strip()))
            for h in self.headers_to_sign if h in r.headers
        ])
        
    def make_content_hash(self, r):
        content_hash = ""
        prepared_body = (r.body or '')
        logger.debug("body is '%s'", prepared_body)

        if r.method == 'POST' and len(prepared_body) > 0:
            logger.debug("signing content: %s", prepared_body)
            if len(prepared_body) > self.max_body:
                logger.debug(
                    "data length %d is larger than maximum %d", 
                    len(prepared_body), self.max_body
                )
                prepared_body = prepared_body[0:self.max_body]
                logger.debug("data truncated to %d for computing the hash", len(prepared_body))

            content_hash = base64_sha256(prepared_body)

        logger.debug("content hash is '%s'", content_hash)
        return content_hash

    def make_data_to_sign(self, r, auth_header):
        if self.testurl:
            testparts = urlparse(self.testurl)
            requestparts = urlparse(r.url)
            url = urlunparse(testparts[0:2] + requestparts[2:])
        else:
            url = r.url

        parsed_url = urlparse(url)
        data_to_sign = '\t'.join([
            r.method,
            parsed_url.scheme,
            parsed_url.netloc,
            # Note: relative URL constraints are handled by requests when it sets up 'r'
            parsed_url.path + ('?' + parsed_url.query if parsed_url.query else ""),
            self.canonicalize_headers(r),
            self.make_content_hash(r),
            auth_header
        ])
        logger.debug('data to sign: %s', '\\t'.join(data_to_sign.split('\t')))
        return data_to_sign

    def sign_request(self, r, timestamp, auth_header):
        return base64_hmac_sha256(
            self.make_data_to_sign(r, auth_header), 
            self.make_signing_key(timestamp)
        )

    def make_auth_header(self, r, timestamp, nonce):
        kvps = [
            ('client_token', self.client_token),
            ('access_token', self.access_token),
            ('timestamp', timestamp),
            ('nonce', nonce),
        ]
        auth_header = "EG1-HMAC-SHA256 " + ';'.join([ "%s=%s" % kvp for kvp in kvps ]) + ';'
        logger.debug('unsigned authorization header: %s', auth_header)
        
        signed_auth_header = auth_header + \
            'signature=' + self.sign_request(r, timestamp, auth_header)

        logger.debug('signed authorization header: %s', signed_auth_header)
        return signed_auth_header

    def __call__(self, r):
        timestamp = eg_timestamp()
        nonce = new_nonce()

        r.headers['Authorization'] = self.make_auth_header(r, timestamp, nonce)
        return r


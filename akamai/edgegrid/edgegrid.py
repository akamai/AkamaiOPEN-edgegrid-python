#!/usr/bin/env python
#
# EdgeGrid requests Auth handler
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

import logging
import uuid
import hashlib
import hmac
import base64
import re
import sys
import os
from requests.auth import AuthBase
from time import gmtime, strftime

if sys.version_info[0] >= 3:
    # python3
    from urllib.parse import urlparse
else:
    # python2.7
    from urlparse import urlparse
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()

logger = logging.getLogger(__name__)

__all__ = ['EdgeGridAuth']


def eg_timestamp():
    return strftime('%Y%m%dT%H:%M:%S+0000', gmtime())


def new_nonce():
    return uuid.uuid4()


def base64_hmac_sha256(data, key):
    return base64.b64encode(
        hmac.new(
            key.encode('utf8'),
            data.encode('utf8'),
            hashlib.sha256).digest()
    ).decode('utf8')


def base64_sha256(data):
    if isinstance(data, str):
        data = data.encode('utf8')
    return base64.b64encode(hashlib.sha256(data).digest()).decode('utf8')


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
                 headers_to_sign=None, max_body=131072):
        """Initialize authentication using the given parameters from the Akamai OPEN APIs
           Interface:

        :param client_token: Client token provided by "Credentials" ui
        :param client_secret: Client secret provided by "Credentials" ui
        :param access_token: Access token provided by "Authorizations" ui
        :param headers_to_sign: An ordered list header names that will be included in
            the signature.  This will be provided by specific APIs. (default [])
        :param max_body: Maximum content body size for POST requests. This will be provided by
            specific APIs. (default 131072)

        """
        self.client_token = client_token
        self.client_secret = client_secret
        self.access_token = access_token
        if headers_to_sign:
            self.headers_to_sign = [h.lower() for h in headers_to_sign]
        else:
            self.headers_to_sign = []
        self.max_body = max_body

        self.redirect_location = None

    @staticmethod
    def from_edgerc(rcinput, section='default'):
        """Returns an EdgeGridAuth object from the configuration from the given section of the
           given edgerc file.

        :param rcinput: EdgeRc instance or path to the edgerc file
        :param section: the section to use (this is the [bracketed] part of the edgerc,
            default is 'default')

        """
        from .edgerc import EdgeRc
        if isinstance(rcinput, EdgeRc):
            rc = rcinput
        else:
            rc = EdgeRc(rcinput)

        return EdgeGridAuth(
            client_token=rc.get(section, 'client_token'),
            client_secret=rc.get(section, 'client_secret'),
            access_token=rc.get(section, 'access_token'),
            headers_to_sign=rc.getlist(section, 'headers_to_sign'),
            max_body=rc.getint(section, 'max_body')
        )

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
                logger.debug(
                    "data truncated to %d for computing the hash",
                    len(prepared_body))

            content_hash = base64_sha256(prepared_body)

        logger.debug("content hash is '%s'", content_hash)
        return content_hash

    def get_header_versions(self, header=None):
        if header is None:
            header = {}

        version_header = ''
        akamai_cli = os.getenv('AKAMAI_CLI')
        akamai_cli_version = os.getenv('AKAMAI_CLI_VERSION')
        if akamai_cli and akamai_cli_version:
            version_header += " AkamaiCLI/" + akamai_cli_version

        akamai_cli_command = os.getenv('AKAMAI_CLI_COMMAND')
        akamai_cli_command_version = os.getenv('AKAMAI_CLI_COMMAND_VERSION')
        if akamai_cli_command and akamai_cli_command_version:
            version_header += " AkamaiCLI-" + akamai_cli_command + \
                "/" + akamai_cli_command_version

        if version_header != '':
            if 'User-Agent' not in header:
                header['User-Agent'] = version_header.strip()
            else:
                header['User-Agent'] += version_header

        return header

    def make_data_to_sign(self, r, auth_header):
        parsed_url = urlparse(r.url)

        if r.headers.get('Host', False):
            netloc = r.headers['Host']
        else:
            netloc = parsed_url.netloc

        self.get_header_versions(r.headers)

        data_to_sign = '\t'.join([
            r.method,
            parsed_url.scheme,
            netloc,
            # Note: relative URL constraints are handled by requests when it
            # sets up 'r'
            parsed_url.path + \
            ('?' + parsed_url.query if parsed_url.query else ""),
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
        auth_header = "EG1-HMAC-SHA256 " + \
            ';'.join(["%s=%s" % kvp for kvp in kvps]) + ';'
        logger.debug('unsigned authorization header: %s', auth_header)

        signed_auth_header = auth_header + \
            'signature=' + self.sign_request(r, timestamp, auth_header)

        logger.debug('signed authorization header: %s', signed_auth_header)
        return signed_auth_header

    def handle_redirect(self, res, **kwargs):
        if res.is_redirect:
            redirect_location = res.headers['location']

            logger.debug("signing the redirected url: %s", redirect_location)
            request_to_sign = res.request.copy()
            request_to_sign.url = redirect_location

            res.request.headers['Authorization'] = self.make_auth_header(
                request_to_sign, eg_timestamp(), new_nonce()
            )

    def __call__(self, r):
        timestamp = eg_timestamp()
        nonce = new_nonce()

        r.headers['Authorization'] = self.make_auth_header(r, timestamp, nonce)
        r.register_hook('response', self.handle_redirect)
        return r

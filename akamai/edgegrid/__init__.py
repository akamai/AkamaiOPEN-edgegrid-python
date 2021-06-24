"""
akamai.edgegrid
~~~~~~~~~~~~~~~

This library provides an authentication handler for Requests that implements the
Akamai {OPEN} EdgeGrid client authentication protocol as
specified by https://developer.akamai.com/introduction/Client_Auth.html.
For more information visit https://developer.akamai.com.

usage:

    >>> import requests
    >>> from akamai.edgegrid import EdgeGridAuth
    >>> from urlparse import urljoin

    >>> baseurl = 'https://akaa-WWWWWWWWWWWW.luna.akamaiapis.net/'
    >>> s = requests.Session()
    >>> s.auth = EdgeGridAuth(
        client_token='akab-XXXXXXXXXXXXXXXXXXXXXXX',
        client_secret='YYYYYYYYYYYYYYYYYYYYYYYYYY',
        access_token='akab-ZZZZZZZZZZZZZZZZZZZZZZZZZZZ'
    )

... now you have a requests session object that can be used to make {OPEN} requests

    >>> result = s.get(urljoin(baseurl, '/diagnostic-tools/v1/locations'))
    >>> result.status_code
    200
    >>> result.json()['locations'][0]
    Hongkong, Hong Kong
"""

from .edgegrid import EdgeGridAuth
from .edgerc import EdgeRc
__all__ = ['EdgeGridAuth', 'EdgeRc']

__title__ = 'edgegrid-python'
__version__ = '1.1'
__author__ = 'Jonathan Landis <jlandis@akamai.com>'
__maintainer__ = 'Akamai Developer Experience team <dl-devexp-eng@akamai.com>'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2021 Akamai Technologies'

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

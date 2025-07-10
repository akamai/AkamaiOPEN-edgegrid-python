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
__version__ = '2.0.2'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2025 Akamai Technologies'

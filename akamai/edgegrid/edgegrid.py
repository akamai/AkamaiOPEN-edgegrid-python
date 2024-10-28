# pylint: disable=too-many-arguments,missing-function-docstring
"""EdgeGrid requests Auth handler"""

import logging
import uuid
import hashlib
import hmac
import base64
import re
import os
from time import gmtime, strftime
from urllib.parse import urlparse

from requests.auth import AuthBase

from .edgerc import EdgeRc

logger = logging.getLogger(__name__)

__all__ = ['EdgeGridAuth']


def eg_timestamp():
    """Generates EdgeGrid compatible timestamp"""
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
    digest = hashlib.sha256(data).digest()
    return base64.b64encode(digest).decode('utf8')


def read_stream_and_rewind(f, max_read):
    """Reads up to read_max bytes from a python file object (like _io.BufferedReader)
    or a MultipartEncoder object, then rewinds the stream.

    The read() method of these objects is decorated by httpie with a side-effect code which
    prints the body content to stdout when the 'B' option is specified for --print. However,
    it does not trigger in the pre-request phase when this plugin is executed. Still, after reading
    we must set the stream position to the beginning to not impact subsequent reads outside
    the plugin. (We don't assume we can be passed a partially read stream to the plugin.)

    Raises TypeError if read() or seek() is not supported by f or f._buffer. May potentially raise
    OSError for any failed I/O operation, in particular io.UnsupportedOperation if the stream is
    not seekable (e.g. is a pipe which we don't expect here as httpie reads pipe contents and
    sets body as bytes).
    """
    try:
        res = f.read(max_read)
    except AttributeError as exc:
        raise TypeError(f'akamai.edgegrid: unexpected body type: {type(f).__name__}') from exc

    try:
        f.seek(0)
    except AttributeError:
        # a MultipartEncoder
        try:
            # During read(), MultipartEncoder lazily loads its upload parts into self._buffer
            # depending on the requested number of bytes. Then a regular read() on self._buffer
            # is performed. Therefore, rewinding self._buffer effectively rewinds the whole
            # MultipartEncoder content.
            # pylint: disable=protected-access
            f._buffer.seek(0)
        except AttributeError as exc:
            raise TypeError(f'akamai.edgegrid: unexpected body type: {type(f).__name__}') from exc
    return res


def read_body_content(body, max_body):
    """The body argument may be one of the following:
    1. bytes object
    2. str object
    3. _io.BufferedReader object for body input from file
    4. requests_toolbelt.MultipartEncoder object for multipart form requests
    5. httpie.uploads.ChunkedUploadStream object for chunked transfer encoding
    (when --chunked, currently not supported)
    May raise TypeError for unexpected input type or OSError for I/O operations.
    """
    if isinstance(body, bytes):
        return body[:max_body]
    if isinstance(body, str):
        return body.encode('utf8')[:max_body]
    return read_stream_and_rewind(body, max_body)


def determine_body_len(body):
    """May raise exception if body appears to be a file (is not a str, bytes or MultipartEncoder)
    but either:
    - has no fileno method (TypeError)
    - raises OSError while trying to calculate the length using the file descriptor"""
    if isinstance(body, bytes):
        return len(body)
    if isinstance(body, str):
        return len(body.encode('utf8'))

    try:
        # a MultipartEncoder?
        return body.len
    except AttributeError:
        # a file object?
        try:
            return os.stat(body.fileno()).st_size
        except AttributeError as exc:
            raise TypeError(
                f'akamai.edgegrid: unexpected body type: {type(body).__name__}') from exc


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
                 *, headers_to_sign=(), max_body=131072):
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
        # pylint: disable=invalid-name
        self.ah = EdgeGridAuthHeaders(
            client_token,
            client_secret,
            access_token,
            headers_to_sign=headers_to_sign,
            max_body=max_body
        )

    @staticmethod
    def from_edgerc(rcinput, section='default'):
        """
        Returns an EdgeGridAuth object from the configuration from the given section
        of the given edgerc file.

        :param rcinput: EdgeRc instance or path to the edgerc file
        :param section: the section to use (this is the [bracketed] part of the edgerc,
            default is 'default')

        """
        if isinstance(rcinput, EdgeRc):
            edgerc = rcinput
        else:
            edgerc = EdgeRc(rcinput)

        return EdgeGridAuth(
            client_token=edgerc.get(section, 'client_token'),
            client_secret=edgerc.get(section, 'client_secret'),
            access_token=edgerc.get(section, 'access_token'),
            headers_to_sign=edgerc.getlist(section, 'headers_to_sign'),
            max_body=edgerc.getint(section, 'max_body')
        )

    def handle_redirect(self, res, **_):
        if res.is_redirect:
            redirect_location = res.headers['location']

            logger.debug("signing the redirected url: %s", redirect_location)
            request_to_sign = res.request.copy()
            request_to_sign.url = redirect_location

            res.request.headers['Authorization'] = self.ah.make_auth_header(
                request_to_sign, eg_timestamp(), new_nonce())

    def __call__(self, r):
        timestamp = eg_timestamp()
        nonce = new_nonce()

        r.headers['Authorization'] = self.ah.make_auth_header(r, timestamp, nonce)
        r.register_hook('response', self.handle_redirect)
        return r


class EdgeGridAuthHeaders:
    """
        A class for preparing requests authentication headers needed for
        Akamai {OPEN} EdgeGrid support.
    """
    def __init__(self, client_token, client_secret, access_token,
                 *, headers_to_sign=(), max_body=131072):
        self.client_token = client_token
        self.client_secret = client_secret
        self.access_token = access_token
        self.headers_to_sign = [h.lower() for h in headers_to_sign]
        self.max_body = max_body

    def make_signing_key(self, timestamp):
        signing_key = base64_hmac_sha256(timestamp, self.client_secret)
        logger.debug('signing key: %s', signing_key)
        return signing_key

    def canonicalize_headers(self, headers):
        spaces_re = re.compile('\\s+')

        # note: r.headers is a case-insensitive dict and self.headers_to_sign
        # should already be in lowercase at this point
        # pylint: disable=consider-using-f-string
        return '\t'.join([
            "%s:%s" % (h, spaces_re.sub(' ', headers[h].strip()))
            for h in self.headers_to_sign if h in headers
        ])

    def make_content_hash(self, body, method):
        logger.debug("body is '%s'", body)
        content_hash = ""
        if method == 'POST':
            buf = read_body_content(body, self.max_body)
            if buf:
                logger.debug("signing content: %s", buf)
                content_hash = base64_sha256(buf)
                try:
                    body_len = determine_body_len(body)
                    if body_len > self.max_body:
                        logger.debug(
                            "data length %d is larger than maximum %d "
                            "and will be truncated for computing the hash",
                            body_len, self.max_body)
                except (TypeError, OSError) as e:
                    # body length is needed only for debugging: just log a possible exception
                    logger.warning("cannot determine length of request body=%s: %s", body, e)
        logger.debug("content hash is '%s'", content_hash)
        return content_hash

    @staticmethod
    def get_header_versions(header=None):
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

    def make_data_to_sign(self, request, auth_header):
        parsed_url = urlparse(request.url)

        if request.headers.get('Host', False):
            netloc = request.headers['Host']
        else:
            netloc = parsed_url.netloc

        self.get_header_versions(request.headers)

        data_to_sign = '\t'.join([
            request.method,
            parsed_url.scheme,
            netloc,
            # Note: relative URL constraints are handled by requests when it sets up 'r'
            parsed_url.path + (';' + parsed_url.params if parsed_url.params else "") +
            ('?' + parsed_url.query if parsed_url.query else ""),
            self.canonicalize_headers(request.headers),
            self.make_content_hash(request.body or '', request.method),
            auth_header
        ])
        logger.debug('data to sign: %s', '\\t'.join(data_to_sign.split('\t')))
        return data_to_sign

    def sign_request(self, request, timestamp, auth_header):
        return base64_hmac_sha256(
            self.make_data_to_sign(request, auth_header),
            self.make_signing_key(timestamp)
        )

    def make_auth_header(self, request, timestamp, nonce):
        kvps = [
            ('client_token', self.client_token),
            ('access_token', self.access_token),
            ('timestamp', timestamp),
            ('nonce', nonce),
        ]
        auth_header = "EG1-HMAC-SHA256 " + \
            ';'.join([f"{k}={v}" for k, v in kvps]) + ';'
        logger.debug('unsigned authorization header: %s', auth_header)

        signed_auth_header = auth_header + \
            'signature=' + self.sign_request(request, timestamp, auth_header)

        logger.debug('signed authorization header: %s', signed_auth_header)
        return signed_auth_header

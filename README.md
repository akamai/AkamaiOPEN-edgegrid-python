# EdgeGrid for Python

This library implements an authentication handler for HTTP [requests](https://requests.readthedocs.io/en/latest/) using the [EdgeGrid authentication](https://techdocs.akamai.com/developer/docs/authenticate-with-edgegrid) scheme.

## Prerequisites
Before you begin, you need to [Create authentication credentials](https://techdocs.akamai.com/developer/docs/set-up-authentication-credentials) in [Control Center](https://control.akamai.com/).

Download the Python release compatible with your operating system at [https://www.python.org/downloads/](https://www.python.org/downloads/).

> Python 2 is no longer supported by the [Python Software Foundation](https://www.python.org/doc/sunset-python-2/).
  However, if you're still using it, you can follow the [Python 2 steps](#python-2-steps).

## Install

1.  Install Python.
    ```
    python setup.py install
    ```

1. Install the developer libraries for Python, SSL and FFI.
    ```
    sudo apt-get install ibssl-dev libffi-dev python-dev
    ```

1. Install the `edgegrid-python` authentication handler.
    ```
    pip install edgegrid-python
    ```

## Make an API call

To use Akamai APIs, you need the values for the tokens from your [.edgerc file](https://techdocs.akamai.com/developer/docs/set-up-authentication-credentials#add-credential-to-edgerc-file).

```pycon
>>> import requests
>>> from akamai.edgegrid import EdgeGridAuth
>>> from urllib.parse import urljoin
>>> baseurl = 'https://akaa-WWWWWWWWWWWW.luna.akamaiapis.net/'
>>> s = requests.Session()
>>> s.auth = EdgeGridAuth(
    client_token='ccccccccccccccccc',
    client_secret='ssssssssssssssssss',
    access_token='aaaaaaaaaaaaaaaaaaaaa'
)

>>> result = s.get(urljoin(baseurl, '/diagnostic-tools/v2/ghost-locations/available'))
>>> result.status_code
200
>>> result.json()['locations'][0]['value']
Oakbrook, IL, United States
...
```

This is an example of an API call to [List available edge server locations](https://techdocs.akamai.com/diagnostic-tools/reference/ghost-locationsavailable). Change the `baseurl` element to reference an endpoint in any of the [Akamai APIs](https://techdocs.akamai.com/home/page/products-tools-a-z?sort=api).

Alternatively, your program can read the credential values directly from the `.edgerc`.

```pycon
>>> import requests
>>> from akamai.edgegrid import EdgeGridAuth, EdgeRc
>>> from urllib.parse import urljoin

>>> edgerc = EdgeRc('~/.edgerc')
>>> section = 'default'
>>> baseurl = 'https://%s' % edgerc.get(section, 'host')

>>> s = requests.Session()
>>> s.auth = EdgeGridAuth.from_edgerc(edgerc, section)

>>> result = s.get(urljoin(baseurl, '/diagnostic-tools/v2/ghost-locations/available'))
>>> result.status_code
200
>>> result.json()['locations'][0]['value']
Oakbrook, IL, United States
...
```

> NOTE: If your `.edgerc` file contains more than one credential set, use the `section` argument to specify which section contains the credentials for your API request.

## Virtual environment

To test in a [virtual environment](https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments), run:

```
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
$ python -m unittest discover
```

### Python 2 steps

Python 2.7 is no longer supported by the [Python Software Foundation](https://www.python.org/doc/sunset-python-2/), but we recognize that some developers continue to use it. If you're using Python 2.7 with EdgeGrid, follow these steps.

1. To upgrade the cryptography package, first run:
    ```
    pip install --upgrade 'cryptography<3.4'
    ```

1. To continue with the installation, run:
    ```
    pip install edgegrid-python
    ```

    or install from sources:
    ```
    python setup.py install
    ```

1. To test, run:
    ```
    $ virtualenv -p python2.7 venv
    $ . venv/bin/activate
    $ pip install 'cryptography<3.4' # just necessary for Python 2.7
    $ pip install -r requirements.txt
    $ python -m unittest discover
    ```

> If you intend to run the examples with Python 2.7, remember that `urljoin` is contained in a different package.
    ```
    from urlparse import urljoin
    ```

## Contribute

1.  Fork the [repository](https://github.com/akamai-open/AkamaiOPEN-edgegrid-python) to modify the **master** branch.
2.  Write a test that demonstrates that the bug was fixed or the feature works as expected.
3.  Send a pull request and nudge the maintainer until it gets merged and published. :)

## Author

Jonathan Landis

## License

> Copyright 2022 Akamai Technologies, Inc. All rights reserved.
>
> Licensed under the Apache License, Version 2.0 (the \"License\"); you
> may not use this file except in compliance with the License. You may
> obtain a copy of the License at
>
> > <http://www.apache.org/licenses/LICENSE-2.0>
>
> Unless required by applicable law or agreed to in writing, software
> distributed under the License is distributed on an \"AS IS\" BASIS,
> WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
> implied. See the License for the specific language governing
> permissions and limitations under the License.

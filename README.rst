EdgeGrid for Python
===================

This library implements an Authentication handler for `requests`_
that provides the `Akamai {OPEN} Edgegrid Authentication`_ scheme. For more information
visit the `Akamai {OPEN} Developer Community`_.

.. code-block:: pycon

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

Alternatively, your program can read the credentials from an .edgerc file.

.. code-block:: pycon

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

If you intend to run the above examples with Python 2.7, remember that urljoin is contained in a different package:

.. code-block:: pycon

    >>> from urlparse import urljoin

.. _`requests`: http://docs.python-requests.org
.. _`Akamai {OPEN} Edgegrid authentication`: https://developer.akamai.com/introduction/Client_Auth.html
.. _`Akamai {OPEN} Developer Community`: https://developer.akamai.com

Installation
------------

**Prerequisite**

For Linux-based distribution, install the developer libraries for Python, SSL and FFI. For example, on Debian-based systems, run:

.. code-block:: bash

    $ sudo apt-get install ibssl-dev libffi-dev python-dev

**To install from pip**

We recommend using any recent Python 3 distribution. Starting from version 3.4 of the cryptography package, Python 2.7 is no longer supported.

If you still want to use Python 2.7, first run:

.. code-block:: bash

    $ pip install --upgrade 'cryptography<3.4'

To continue with the installation:

.. code-block:: bash

    $ pip install edgegrid-python

**To install from sources**

.. code-block:: bash

    $ python setup.py install

**To run tests**

Both Python 2 and Python 3 are supported. This example uses Python 2.7. Run:

.. code-block:: bash

    $ virtualenv -p python2.7 venv
    $ . venv/bin/activate
    $ pip install 'cryptography<3.4' # just necessary for Python 2.7
    $ pip install -r requirements.txt
    $ python -m unittest discover

For Python 3.3 or newer, replace the `virtualenv` module with `venv`. Run:

.. code-block:: bash

    $ python3 -m venv venv
    $ . venv/bin/activate
    $ pip install -r requirements.txt
    $ python -m unittest discover

Creating your own .edgerc
----------

#. Copy the `akamai/edgegrid/test/sample_edgerc` file to your home directory and rename as `.edgerc`.
#. Edit the copied file and provide your own credentials. For more information on creating an `.edgerc` file, see `Get started  with APIs`_.

.. _`Get started  with APIs`: https://developer.akamai.com/api/getting-started#edgercfile

Contribute
----------

#. Fork `the repository`_ to start making your changes to the **master** branch
#. Write a test which shows that the bug was fixed or that the feature works as expected.
#. Send a pull request and bug the maintainer until it gets merged and published.  :)

.. _`the repository`: https://github.com/akamai-open/AkamaiOPEN-edgegrid-python

Author
------

Jonathan Landis

License
-------

   Copyright 2021 Akamai Technologies, Inc. All rights reserved.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

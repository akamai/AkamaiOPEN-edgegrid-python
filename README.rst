EdgeGrid for Python
===================

This library implements an Authentication handler for `requests`_
that provides the `Akamai {OPEN} Edgegrid Authentication`_ scheme. For more information
visit the `Akamai {OPEN} Developer Community`_.

.. code-block:: pycon

    >>> import requests
    >>> from akamai.edgegrid import EdgeGridAuth
    >>> from urlparse import urljoin
    >>> baseurl = 'https://akaa-WWWWWWWWWWWW.luna.akamaiapis.net/'
    >>> s = requests.Session()
    >>> s.auth = EdgeGridAuth(
        client_token='ccccccccccccccccc',
        client_secret='ssssssssssssssssss',
        access_token='aaaaaaaaaaaaaaaaaaaaa'
    )

    >>> result = s.get(urljoin(baseurl, '/diagnostic-tools/v1/locations'))
    >>> result.status_code
    200
    >>> result.json()['locations'][0]
    Hongkong, Hong Kong
    ...

Alternatively, your program can read the credentials from an .edgerc file.

.. code-block:: pycon

    >>> import requests
    >>> from akamai.edgegrid import EdgeGridAuth, EdgeRc
    >>> from urlparse import urljoin

    >>> edgerc = EdgeRc('credentials.edgerc')
    >>> section = 'default'
    >>> baseurl = 'https://%s' % edgerc.get(section, 'host')

    >>> s = requests.Session()
    >>> s.auth = EdgeGridAuth.from_edgerc(edgerc, section)

    >>> result = s.get(urljoin(baseurl, '/diagnostic-tools/v1/locations'))
    >>> result.status_code
    200
    >>> result.json()['locations'][0]
    Hongkong, Hong Kong
    ...

.. _`requests`: http://docs.python-requests.org
.. _`Akamai {OPEN} Edgegrid authentication`: https://developer.akamai.com/introduction/Client_Auth.html
.. _`Akamai {OPEN} Developer Community`: https://developer.akamai.com

Installation
------------

To install from pip:

.. code-block:: bash

    $ pip install edgegrid-python

To install from sources:

.. code-block:: bash

    $ python setup.py install

To run tests:

.. code-block:: bash

    $ virtualenv -p python2.7 venv
    $ . venv/bin/activate
    $ pip install -r requirements.txt
    $ python -m unittest discover

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

   Copyright 2015 Akamai Technologies, Inc. All rights reserved. 

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

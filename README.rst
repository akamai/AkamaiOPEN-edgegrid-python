EdgeGrid for Python
===================

This library implements an Authentication handler for `requests`_
that provides the `Akamai {OPEN} Edgegrid Authentication`_ scheme. For more infomation
visit the `Akamai {OPEN} Developer Community`_.

.. code-block:: pycon

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

    >>> result = s.get(urljoin(baseurl, '/diagnostic-tools/v1/locations'))
    >>> result.status_code
    200
    >>> result.json()['locations'][0]
    Hongkong, Hong Kong
    ...

.. _`requests`: http://docs.python-requests.org
.. _`Akamai {OPEN} Edgegrid authentication`: https://developer.akamai.com/stuff/Getting_Started_with_OPEN_APIs/Client_Auth.html
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

   Copyright 2014 Akamai Technologies, Inc. All rights reserved. 

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

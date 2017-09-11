.. :changelog:

History
-------

1.1.0 (2017-09-11)
++++++++++++++++++

- better python3 support


1.0.9 (2015-07-29)
++++++++++++++++++

- update default max_body to be 128k
- read both max_body and max-body style properties from edgerc files

1.0.8 (2015-06-23)
++++++++++++++++++

- update requests dependency version


1.0.7 (2015-06-11)
++++++++++++++++++

- use pyopenssl to improve security as per https://urllib3.readthedocs.org/en/latest/security.html#pyopenssl

1.0.6 (2015-02-28)
++++++++++++++++++

- support passing in EdgeRc to from_edgerc static method
- fix problem with following redirects

1.0.5 (2014-11-10)
++++++++++++++++++

- support 'Host' header more transparently
- remove testurl since new 'Host' support handles the same case
- support edgerc file

1.0.4 (2014-11-05)
++++++++++++++++++

- support python3

1.0.3 (2014-10-16)
++++++++++++++++++

- update link to developer site

1.0.2 (2014-08-29)
++++++++++++++++++

- add testurl parameter for overriding method and host for testing

1.0.1 (2014-05-14)
++++++++++++++++++

- Change POST behavior to truncate and max_body to 128kb(GRID-236)

1.0 (2014-04-04)
++++++++++++++++
- First version

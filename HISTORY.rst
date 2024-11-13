.. :changelog:

History
-------

2.0.0 (2024-11-13)
++++++++++++++++++

* Breaking changes
    - discontinue support for Python 2.7, the minimum supported version is now Python 3.9
    - the ``__init__`` function of ``EdgeGridAuth`` and ``EdgeGridAuthHeaders`` now accepts ``headers_to_sign`` and ``max_body`` as keyword-only arguments
    - change signatures of these methods in the ``EdgeGridAuthHeaders`` class: ``make_auth_header``, ``sign_request`` and ``make_data_to_sign``

* Improvements
    - update several dependencies in ``setup.py``
    - start generating files ``requirements.txt`` and ``dev-requirements.txt`` using ``pip-compile``,
      so that they contain the full set of project dependencies

* Bug fixes
    - fix handling file objects in the request body for ``EdgeGridAuth``

1.3.1 (2022-09-22)
++++++++++++++++++

* Bug fixes
    - `GH#51 <https://github.com/akamai/AkamaiOPEN-edgegrid-python/issues/51>`_: include path params in signed path

1.3.0 (2022-08-29)
++++++++++++++++++

* Improvements
    - decouple from `requests` library
    - add support for MultipartEncoder

* Bug fixes
    - remove unnecessary shebangs and permissions

1.2.1 (2021-10-11)
++++++++++++++++++

* Bug fixes
    - `GH#36 <https://github.com/akamai/AkamaiOPEN-edgegrid-python/issues/36>`_, `GH#44 <https://github.com/akamai/AkamaiOPEN-edgegrid-python/issues/44>`_ and `GH#53 <https://github.com/akamai/AkamaiOPEN-edgegrid-python/issues/53>`_ issues: split `MANIFEST.in` in several lines to properly include in Python package all necessary resource files

1.2.0 (2021-08-10)
++++++++++++++++++

* Bug fixes
    - `GH#48 <https://github.com/akamai/AkamaiOPEN-edgegrid-python/issues/48>`_ and `GH#50 <https://github.com/akamai/AkamaiOPEN-edgegrid-python/issues/50>`_ issues: recognize the `~` tilde character as home directory alias
    - `GH#36 <https://github.com/akamai/AkamaiOPEN-edgegrid-python/issues/36>`_, `GH#44 <https://github.com/akamai/AkamaiOPEN-edgegrid-python/issues/44>`_ and `GH#53 <https://github.com/akamai/AkamaiOPEN-edgegrid-python/issues/53>`_ issues: add missing test resource files to PyPI package
    - `GH#41 <https://github.com/akamai/AkamaiOPEN-edgegrid-python/issues/41>`_: require PyOpenSSL >= v19.0.0 to avoid old OS packages

* Improvements
    - better Python 2 and Python 3 documentation and related setup.py tags

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

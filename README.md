# EdgeGrid for Python

This library implements an Authentication handler for [HTTP requests](https://requests.readthedocs.io/en/latest/) using the [Akamai EdgeGrid Authentication](https://techdocs.akamai.com/developer/docs/authenticate-with-edgegrid) scheme for Python.

## Install

To use the library, you need to have Python 3.9 or later installed on your system. You can download it from [https://www.python.org/downloads/](https://www.python.org/downloads/).

> __NOTE:__ Python 2 is no longer supported by the [Python Software Foundation](https://www.python.org/doc/sunset-python-2/). You won't be able to use the library with Python 2.

Then, install the `edgegrid-python` authentication handler from sources by running this command from the project root directory:

   ```
   pip install .
   ```

Alternatively, you can install it from PyPI (Python Package Index) by running:

```
pip install edgegrid-python
```

## Authentication

We provide authentication credentials through an API client. Requests to the API are signed with a timestamp and are executed immediately.

1. [Create authentication credentials](https://techdocs.akamai.com/developer/docs/set-up-authentication-credentials).

2. Place your credentials in an EdgeGrid resource file, `.edgerc`, under a heading of `[default]` at your local home directory.

   ```
    [default]
    client_secret = C113nt53KR3TN6N90yVuAgICxIRwsObLi0E67/N8eRN=
    host = akab-h05tnam3wl42son7nktnlnnx-kbob3i3v.luna.akamaiapis.net
    access_token = akab-acc35t0k3nodujqunph3w7hzp7-gtm6ij
    client_token = akab-c113ntt0k3n4qtari252bfxxbsl-yvsdj
    ```

3. Use your local `.edgerc` by providing the path to your resource file and credentials' section header.
   
   ```python
    import requests
    from akamai.edgegrid import EdgeGridAuth, EdgeRc

    edgerc = EdgeRc('~/.edgerc')
    section = 'default'
    baseurl = 'https://%s' % edgerc.get(section, 'host')

    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(edgerc, section)
   ```
   Or hard code them as variables.
   
   ```python
    import requests
    from akamai.edgegrid import EdgeGridAuth

    session = requests.Session()
    session.auth = EdgeGridAuth(
        client_token='akab-c113ntt0k3n4qtari252bfxxbsl-yvsdj',
        client_secret='C113nt53KR3TN6N90yVuAgICxIRwsObLi0E67/N8eRN=',
        access_token='akab-acc35t0k3nodujqunph3w7hzp7-gtm6ij'
    )
   ```

## Use

To use the library, provide the path to your `.edgerc`, your credentials section header, and the appropriate endpoint information.

```python
import requests
import json
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urljoin

edgerc = EdgeRc('~/.edgerc')
section = 'default'
baseurl = 'https://%s' % edgerc.get(section, 'host')

session = requests.Session()
session.auth = EdgeGridAuth.from_edgerc(edgerc, section)

path = '/identity-management/v3/user-profile'
headers = {
  "Accept": "application/json"
} 
querystring = {
  "actions": True,
  "authGrants": True,
  "notifications": True
}  

result = session.get(urljoin(baseurl, path), headers=headers, params=querystring)
print(result.status_code)
print(json.dumps(result.json(), indent=2))
```

### Query string parameters

When entering query parameters use the `querystring` property. Set up the parameters as name-value pairs in an object.

```python
edgerc = EdgeRc('~/.edgerc')
section = 'default'
baseurl = 'https://%s' % edgerc.get(section, 'host')

session = requests.Session()
session.auth = EdgeGridAuth.from_edgerc(edgerc, section)

path = '/identity-management/v3/user-profile'
querystring = {
  "actions": True,
  "authGrants": True,
  "notifications": True
}  

result = session.get(urljoin(baseurl, path), params=querystring)
```

### Headers

Enter request headers in the `headers` property as name-value pairs in an object.

> __NOTE:__ You don't need to include the `Content-Type` and `Content-Length` headers. The authentication layer adds these values.

```python
edgerc = EdgeRc('~/.edgerc')
section = 'default'
baseurl = 'https://%s' % edgerc.get(section, 'host')

session = requests.Session()
session.auth = EdgeGridAuth.from_edgerc(edgerc, section)

path = '/identity-management/v3/user-profile'
headers = {
  "Accept": "application/json"
} 

result = session.get(urljoin(baseurl, path), headers=headers)
```

### Body data

Provide the request body as an object in the `payload` property.

```python
edgerc = EdgeRc('~/.edgerc')
section = 'default'
baseurl = 'https://%s' % edgerc.get(section, 'host')

session = requests.Session()
session.auth = EdgeGridAuth.from_edgerc(edgerc, section)

path = '/identity-management/v3/user-profile/basic-info'
payload = {
    "contactType": "Billing",
    "country": "USA",
    "firstName": "John",
    "lastName": "Smith",
    "preferredLanguage": "English",
    "sessionTimeOut": 30,
    "timeZone": "GMT",
    "phone": "3456788765"
}

result = session.put(urljoin(baseurl, path), json=payload)
```

As the `data` parameter for the `session` methods, EdgeGrid for Python
currently supports the `bytes` and `requests_toolbelt.MultipartEncoder`
types or a file-like object.

### Debug

Enable debugging to get additional information about a request.

To log requests, use the built-in request logging. Add this before making a request:

```python
import logging
from http.client import HTTPConnection
HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
urllib_log = logging.getLogger("urllib3")
urllib_log.setLevel(logging.DEBUG)
urllib_log.propagate = True
```

This will print everything apart from the HTTP response body. See the [Requests library for Python](https://requests.readthedocs.io/en/latest/api/#api-changes) for the original recipe.

To log specific parts like URL, status code, headers, or body, add this:

```python
import requests
import logging
import json
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urljoin

logger = logging.getLogger('requests_logger')
logging.basicConfig(level=logging.DEBUG)

edgerc = EdgeRc('~/.edgerc')
section = 'default'
baseurl = 'https://%s' % edgerc.get(section, 'host')

session = requests.Session()
session.auth = EdgeGridAuth.from_edgerc(edgerc, section)

path = '/identity-management/v3/user-profile'

result = session.get(urljoin(baseurl, path))
logger.debug(f'URL: {result.url}')
logger.debug(f'Status Code: {result.status_code}')
logger.debug(f'Headers: {result.headers}')
logger.debug(f'Body: {result.json()}')
```

## Virtual environment

A [virtual environment](https://docs.python.org/3/library/venv.html) is a tool to keep dependencies required by different projects in separate places. The `venv` module is included in Python 3 by default.

Set up a virtual environment:

1. Initialize your environment in a new directory.

   ```
   // Unix/macOS
   python3 -m venv ~/Desktop/myenv

   // Windows
   py -m venv ~/Desktop/myenv
   ```

   This creates a `venv` in the specified directory as well as copies pip into it.

2. Activate your environment.
   
   ```
   // Unix/macOS
   source ~/Desktop/myenv/bin/activate

   // Windows
   ~/Desktop/myenv/Scripts/activate
   ```

   Your prompt will change to show you're working in a virtual environment, for example:

   ```
   (myenv) jsmith@abc-de12fg $
   ```

3. To recreate the environment, install the required dependencies within your project.

   ```
   pip install -r dev-requirements.txt
   ```

4. Run the tests.

   ```
   // Unix/macOS
   pytest -v

   // Windows
   py -m pytest -v
   ```

5. To deactivate your environment, run the `deactivate` command.

## Reporting issues

To report an issue or make a suggestion, create a new [GitHub issue](https://github.com/akamai/AkamaiOPEN-edgegrid-python/issues).

## License

Copyright 2025 Akamai Technologies, Inc. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use these files except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

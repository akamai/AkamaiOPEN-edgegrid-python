# This example creates your new API client credentials.
#
# To run this example:
#
# 1. Specify the location of your .edgerc file and the section header of the set of credentials to use.
#
## The defaults here expect the .edgerc at your home directory and use the credentials under the heading of default.
#
# 2. Open a Terminal or shell instance and run "python examples/create-credentials.py".
#
# A successful call returns a new API client with its credentialId. Use this ID in both the update and delete examples.
#
# For more information on the call used in this example, see https://techdocs.akamai.com/iam-api/reference/post-self-credentials.

import requests
import json
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urljoin

edgerc = EdgeRc('~/.edgerc')
section = 'default'
baseurl = 'https://%s' % edgerc.get(section, 'host')

session = requests.Session()
session.auth = EdgeGridAuth.from_edgerc(edgerc, section)

path = '/identity-management/v3/api-clients/self/credentials'
headers = {
  "Accept": "application/json"
}

result = session.post(urljoin(baseurl, path), headers=headers)
print(result.status_code)
print(json.dumps(result.json(), indent=2))
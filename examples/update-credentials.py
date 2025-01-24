# This example updates the credentials from the create credentials example.
#
# To run this example:
#
# 1. Specify the location of your .edgerc file and the section header of the set of credentials to use.
#
# The defaults here expect the .edgerc at your home directory and use the credentials under the heading of default.
#
# 2. Add the credentialId for the set of credentials created using the create example as a path parameter.
#
# 3. Edit the expiresOn date to today's date. Optionally, you can change the description value.
#
# **Important:** Don't use the credentials you're actively using when inactivating a set of credentials. Otherwise, you'll block your access to the Akamai APIs.
#
# 4. Open a Terminal or shell instance and run "python examples/update-credentials.py".
#
# A successful call returns.
#
# For more information on the call used in this example, see https://techdocs.akamai.com/iam-api/reference/put-self-credential.

import requests
import json
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urljoin

edgerc = EdgeRc('~/.edgerc')
section = 'default'
baseurl = 'https://%s' % edgerc.get(section, 'host')

session = requests.Session()
session.auth = EdgeGridAuth.from_edgerc(edgerc, section)
credentialId = 123456

path = '/identity-management/v3/api-clients/self/credentials/{}'.format(credentialId)
headers = {
  "Content-Type": "application/json",
  "Accept": "application/json"}
payload = {
    "status": "INACTIVE",
    "expiresOn": "2024-12-30T22:09:24.000Z", # The date cannot be more than two years out or it will return a 400
    "description": "Update this credential"
}

result = session.put(urljoin(baseurl, path), headers=headers, json=payload)
print(result.status_code)
print(json.dumps(result.json(), indent=2))


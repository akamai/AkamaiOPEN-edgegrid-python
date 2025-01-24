# This example deletes your API client credentials.
#
# To run this example:
#
# 1. Specify the location of your .edgerc file and the section header of the set of credentials to use.
#
# The defaults here expect the .edgerc at your home directory and use the credentials under the heading of default.
#
# 2. Add the credentialId from the update example to the path. You can only delete inactive credentials. Sending the request on an active set will return a 400. Use the update credentials example for deactivation.
#
# **Important:** Don't use the credentials you're actively using when deleting a set of credentials. Otherwise, you'll block your access to the Akamai APIs.
#
# 3. Open a Terminal or shell instance and run "python examples/delete-credentials.py".
#
# A successful call returns "" null.
#
# For more information on the call used in this example, see https://techdocs.akamai.com/iam-api/reference/delete-self-credential.

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

result = session.delete(urljoin(baseurl, path))
print(result.status_code)
#!/usr/bin/env python
#
# support for .edgerc file format
#
# Copyright 2021 Akamai Technologies, Inc. All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import sys
from os.path import expanduser

if sys.version_info[0] >= 3:
    # python3
    from configparser import ConfigParser
else:
    # python2.7
    from ConfigParser import ConfigParser


logger = logging.getLogger(__name__)


class EdgeRc(ConfigParser):
    def __init__(self, filename):
        ConfigParser.__init__(self,
                              {'client_token': '',
                               'client_secret': '',
                               'host': '',
                               'access_token': '',
                               'max_body': '131072',
                               'headers_to_sign': 'None'})
        logger.debug("loading edgerc from %s", filename)

        self.read(expanduser(filename))

        logger.debug("successfully loaded edgerc")

    def optionxform(self, optionstr):
        """support both max_body and max-body style keys"""
        return optionstr.replace('-', '_')

    def getlist(self, section, option):
        """
            returns the named option as a list, splitting the original value
            by ','
        """
        value = self.get(section, option)
        if value:
            return value.split(',')
        else:
            return None

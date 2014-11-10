#!/usr/bin/env python
#
# support for .edgerc file format
#
# Copyright 2014 Akamai Technologies, Inc. All Rights Reserved
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

if sys.version_info[0] >= 3:
    # python3
    from configparser import ConfigParser
else:
    # python2.7
    from ConfigParser import ConfigParser


logger = logging.getLogger(__name__)

class EdgeRc(ConfigParser):
    required_options = ['client_token', 'client_secret', 'host', 'access_token']

    def __init__(self, filename):
        ConfigParser.__init__(self, {'max_body': '2048', 'headers_to_sign': None})
        logger.debug("loading edgerc from %s", filename)

        self.read(filename)
        self.validate()

        logger.debug("successfully loaded edgerc")

    def validate(self):
        def validate_section(section):
            missing = []
            for opt in self.required_options:
                try:
                    self.get(section, opt)
                except:
                    missing.append(opt)

            if len(missing) > 0:
                raise Exception("Missing required options: %s" % missing)

        for section in self.sections():
            validate_section(section)

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

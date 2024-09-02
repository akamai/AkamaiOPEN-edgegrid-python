"""Support for .edgerc file format"""

import logging
from configparser import ConfigParser
from os.path import expanduser

logger = logging.getLogger(__name__)


class EdgeRc(ConfigParser):
    """Class for managing .edgerc files"""
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
            returns the named option as a list, splitting the original value by ','
        """
        value = self.get(section, option)
        if value:
            return value.split(',')
        return None

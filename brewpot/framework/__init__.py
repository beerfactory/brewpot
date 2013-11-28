#!/usr/bin/env python
# -- Content-Encoding: UTF-8 --

from brewpot import utils

BundleState = utils.enum(UNINSTALLED=0x01, INSTALLED=0x02, RESOLVED=0x04, STARTING=0x08, STOPPING=0x10, ACTIVE=0x20)

class Bundle(object):
    _state = None

    def __init__(self):
        pass

    @property
    def state(self):
        """
        Get bundle state
        """
        return self._state
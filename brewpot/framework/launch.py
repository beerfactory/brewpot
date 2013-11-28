#!/usr/bin/env python
# -- Content-Encoding: UTF-8 --
"""
Launch framework module
"""

import abc
from brewpot.framework import Bundle
from brewpot.framework.impl import FrameworkImpl

class Framework(Bundle):
    #@abc.abstractmethod
    pass

class FrameworkFactory(object):
    @classmethod
    def newFramework(cls, configuration):
        if not hasattr(cls, 'frameworks'):
            cls.frameworks = {}
        fwk = FrameworkImpl(configuration)



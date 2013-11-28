#!/usr/bin/env python
# -- Content-Encoding: UTF-8 --
"""
Framework implementation
"""

from brewpot.framework.launch import Framework
from brewpot.framework import BundleState
import uuid

class FrameworkImpl(Framework):
    def __init__(self, properties):
        self._state = BundleState.INSTALLED

        # Framework properties
        if not isinstance(properties, dict):
            self._properties = {}
        else:
            self._properties = properties.copy()

        #Init framework UUID
        self.uid = str(uuid.uuid4())
        pass
# -*- mode: python; coding: utf-8 -*-
#
# FirePython server-side support library
#
# for usage see README.markdown or http://github.com/woid/firepython
#

import re

__version__ = '0.3'

FIRELOGGER_VERSION_HEADER = 'HTTP_X_FIRELOGGER'
FIRELOGGER_AUTH_HEADER    = 'HTTP_X_FIRELOGGERAUTH'
FIRELOGGER_RESPONSE_HEADER = re.compile(r'^FireLogger', re.IGNORECASE)

DEEP_LOCALS = True
RAZOR_MODE = False
JSONPICKLE_DEPTH = 8

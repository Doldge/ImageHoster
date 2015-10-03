#! /usr/bin/python

import sys

path = '/var/www/backend.southisland/'
if path not in sys.path:
        sys.path.append(path)

from index import app as application


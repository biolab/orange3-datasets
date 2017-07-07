"""Basic testing package.

This package inits a dummy Qt app so that we have an active thread when
creating random widgets in unit tests.
"""

import sys

from AnyQt import QtGui

DUMMY_APP = QtGui.QApplication(sys.argv)

# -*- coding: utf-8 -*-
"""PyVISA testsuite.

"""
import logging
import os
import unittest
from logging.handlers import BufferingHandler

from pyvisa import ResourceManager, logger

try:
    ResourceManager()
except ValueError:
    VISA_PRESENT = False
else:
    VISA_PRESENT = True

require_visa_lib = unittest.skipUnless(
    VISA_PRESENT, "Requires an installed VISA library. Run on PyVISA " "buildbot."
)


class TestHandler(BufferingHandler):
    def __init__(self, only_warnings=False):
        # BufferingHandler takes a "capacity" argument
        # so as to know when to flush. As we're overriding
        # shouldFlush anyway, we can set a capacity of zero.
        # You can call flush() manually to clear out the
        # buffer.
        self.only_warnings = only_warnings
        BufferingHandler.__init__(self, 0)

    def shouldFlush(self, record):
        return False

    def emit(self, record):
        if self.only_warnings and record.level != logging.WARNING:
            return
        self.buffer.append(record.__dict__)


class BaseTestCase(unittest.TestCase):

    CHECK_NO_WARNING = True

    def setUp(self):
        self._test_handler = None
        if self.CHECK_NO_WARNING:
            self._test_handler = th = TestHandler()
            th.setLevel(logging.WARNING)
            logger.addHandler(th)

    def tearDown(self):
        if self._test_handler is not None:
            buf = self._test_handler.buffer
            length = len(buf)
            msg = "\n".join(record.get("msg", str(record)) for record in buf)
            self.assertEqual(length, 0, msg="%d warnings raised.\n%s" % (length, msg))


def testsuite():
    """A testsuite that has all the pyvisa tests.

    """
    return unittest.TestLoader().discover(os.path.dirname(__file__))


def main():
    """Runs the testsuite as command line application.

    """
    try:
        unittest.main()
    except Exception as e:
        print("Error: %s" % e)


def run():
    """Run all tests.

    :return: a :class:`unittest.TestResult` object

    """
    test_runner = unittest.TextTestRunner()
    return test_runner.run(testsuite())

# Copyright (c) 2002-2004 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.3 $
import unittest
import Zope

try:
    from Zope import startup
    startup()
except ImportError:
    # startup is only in Zope2.6
    pass

from Products.Formulator.tests import test_Form, test_validators, test_serialize

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(test_Form.test_suite())
    suite.addTest(test_validators.test_suite())
    suite.addTest(test_serialize.test_suite())
    return suite

def main():
    unittest.TextTestRunner(verbosity=1).run(test_suite())

if __name__ == '__main__':
    main()

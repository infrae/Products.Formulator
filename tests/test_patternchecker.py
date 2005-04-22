from Products.Formulator.PatternChecker import PatternChecker

import unittest

class PatternCheckerTest(unittest.TestCase):

    def setUp(self):
        self.val = PatternChecker()

    def assertValueMatches(self, patterns, value):
        self.assertEquals(value, \
                          self.val.validate_value(patterns, value))
    def assertValueChanged(self, patterns, value, result):
        self.assertEquals(result, \
                          self.val.validate_value(patterns, value))

    def test_some_patterns(self):
        as = self.assertValueMatches
        asd = self.assertValueChanged

        # American long ZIP
        as(['ddddd-dddd'], '34567-1298')
        asd(['ddddd-dddd'], '  34567-1298  \t  ', '34567-1298' )
 
        # American phone number
        as(['(ddd) ddd-dddd', 'ddd-ddd-dddd','ddd ddd-dddd'],
           '(345) 678-1298')
        asd(['(ddd) ddd-dddd', 'ddd-ddd-dddd', 'ddd ddd-dddd'],
            '345-678-1298','(345) 678-1298')
        
        # American money
        as(['$ d*.dd'], '$ 1345345.00')
        #as(['$ d*.dd'], '$  1345345,00 ', '$ 1345345.00')
        
        # German money
        as(['d*.dd DM'], '267.98 DM')

        # German license plate
        as(['eee ee-ddd'], 'OSL HR-683')

        # German phone number (international)
        as(['+49 (d*) d*'], '+49 (3574) 7253')
        asd(['+49 (d*) d*'], '+49  (3574)  7253', '+49 (3574) 7253')


    def test_multiple_ffs(self):
        for c in ('a','b','c','d','e','f'):
            self.assertValueMatches(['f-f'], '%s-1'%c)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PatternCheckerTest, 'test'))
    return suite

if __name__ == '__main__':
    framework()


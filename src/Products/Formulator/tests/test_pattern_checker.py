# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt


import unittest

from Products.Formulator.PatternChecker import PatternChecker


class PatternCheckerTest(unittest.TestCase):

    def setUp(self):
        self.val = PatternChecker()

    def assertValueMatches(self, patterns, value):
        self.assertEqual(value, self.val.validate_value(patterns, value))

    def assertValueChanged(self, patterns, value, result):
        self.assertEqual(result, self.val.validate_value(patterns, value))

    def test_some_patterns(self):
        vOk = self.assertValueMatches
        mOk = self.assertValueChanged

        # American long ZIP
        vOk(['ddddd-dddd'], '34567-1298')
        mOk(['ddddd-dddd'], '  34567-1298  \t  ', '34567-1298')

        # American phone number
        vOk(['(ddd) ddd-dddd', 'ddd-ddd-dddd', 'ddd ddd-dddd'],
            '(345) 678-1298')
        mOk(['(ddd) ddd-dddd', 'ddd-ddd-dddd', 'ddd ddd-dddd'],
            '345-678-1298', '(345) 678-1298')

        # American money
        vOk(['$ d*.dd'], '$ 1345345.00')
        # mOk(['$ d*.dd'], '$  1345345,00 ', '$ 1345345.00')

        # German money
        vOk(['d*.dd DM'], '267.98 DM')

        # German license plate
        vOk(['eee ee-ddd'], 'OSL HR-683')

        # German phone number (international)
        vOk(['+49 (d*) d*'], '+49 (3574) 7253')
        mOk(['+49 (d*) d*'], '+49  (3574)  7253', '+49 (3574) 7253')

    def test_multiple_ffs(self):
        for c in ('a', 'b', 'c', 'd', 'e', 'f'):
            self.assertValueMatches(['f-f'], '%s-1' % c)

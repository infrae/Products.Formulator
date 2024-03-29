# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

""" random assembly testing some reported bugs.
    This is _not_ a structured or even complete test suite.
    Most tests test the "render" method of fields, thus they
    maybe could be moved to a "test_widgets" test case partially
"""

import unittest

from Products.Formulator.testing import FunctionalLayer


class FieldIdsTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.layer.login('manager')
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Formulator']
        factory.manage_add('form', 'Test Form')
        self.form = self.root.form
        factory = self.form.manage_addProduct['Formulator']
        factory.manage_addField('text', 'Text Field', 'StringField')

    def test_field_html_id(self):
        # test standard use-case
        sf = self.form.text
        self.assertEqual('field-text', sf.generate_field_html_id())
        self.assertEqual('field-text', sf.html_id)

    def test_html_id_with_field_record(self):
        # SilvaMetadata uses a 'field_record' to add uniqueness
        # to the field key, so test that as well
        sf = self.form.text
        self.assertEqual('field-text', sf.generate_field_html_id())

        sf.field_record = 'silva-extra'
        self.assertEqual('silva-extra-text-record',
                         sf.generate_field_html_id())

        sf.field_record = None

    def test_html_id_with_field_record_bis(self):
        # the form name can be used to add uniqueness as well
        # to the field key, so test that as well
        sf = self.form.text
        self.assertEqual('field-text', sf.generate_field_html_id())

        self.form.name = 'test'
        self.assertEqual('testfield-text', sf.generate_field_html_id())
        self.form.name = ''

    def test_html_id_in_extra(self):
        # verify that an html id specified in the "extra" parameter
        # is used if present.  Also test the regular expression
        sf = self.form.text
        sf.values['extra'] = 'id="HTML"'
        self.assertEqual('HTML', sf.generate_field_html_id())
        sf.values['extra'] = "id='HTML'"
        self.assertEqual('HTML', sf.generate_field_html_id())
        sf.values['extra'] = 'class="blah123" id="HTML"'
        self.assertEqual('HTML', sf.generate_field_html_id())
        sf.values['extra'] = 'formid="asdf" id="HTML"'
        self.assertEqual('HTML', sf.generate_field_html_id())
        sf.values['extra'] = 'id="HTML" formid="asdf"'
        self.assertEqual('HTML', sf.generate_field_html_id())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FieldIdsTestCase))
    return suite

# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt
""" random assembly testing some reported bugs.
    This is _not_ a structured or even complete test suite.
    Most tests test the "render" method of fields, thus they
    maybe could be moved to a "test_widgets" test case partially
"""

import re
import unittest
from xml.dom.minidom import parseString

from DateTime import DateTime
from Products.PythonScripts.PythonScript import PythonScript

from Products.Formulator.MethodField import Method
from Products.Formulator.TALESField import TALESMethod
from Products.Formulator.testing import FunctionalLayer
from Products.Formulator.testing import TestRequest


class FormTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.layer.login('manager')
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Formulator']
        factory.manage_add('form', 'Test Form')
        self.form = self.root.form

    def test_has_field(self):
        """ test if has_field works, if one asks for a non-field attribute.
            this has raised AttributeError "aq_explicit" in previous versions
        """
        self.assertFalse(self.form.has_field('title'))

    def test_list_items(self):
        self._test_list_items('ListField')

    def test_multi_list_items(self):
        self._test_list_items('MultiListField')

    def _test_list_items(self, list_field_type):
        """ test if a list of values returned by TALES (override) expressions
        is interpreted properly.
        If a TALES tab returns a sequence of items and some item is
        actually a string of length 2 (e.g. "ok"), this previously
        has lead to a item text of 'o' and a display value of 'k'
        (as the this is actually a sequence of length 2 ...)
         See http://sourceforge.net/mailarchive/forum.php?thread_id=1359918&forum_id=1702
        """  # noqa: E501 line too long

        self.form.manage_addField(
            'list_field',
            'Test List Field',
            list_field_type)

        self.form.override_test = PythonScript('override_test')
        self.form.override_test.write("return ['ok', 'no']\n")

        list_field = self.form.list_field
        list_field.values['items'] = [('ok', 'ok'), ('no', 'no')]

        list_field.values['first_item'] = 'on'

        items1 = list_field.render()

        # test TALES
        list_field.tales['items'] = TALESMethod("python:['ok', 'no']")
        items2 = list_field.render()

        # test render
        self.assertEqual(items1, items2)
        # test render_view
        self.assertEqual('ok', list_field.render_view('ok'))
        # test validation ... fake request with a dictionary ...
        list_field.validate({'field_list_field': 'ok'})

        # test override (most probably superfluous)
        del list_field.tales['items']
        list_field.overrides['items'] = Method('override_test')
        items2 = list_field.render()

        self.assertEqual(items1, items2)

        # missing: if returning a list of int,
        # rendering does work here, but validation fails.
        # maybe it should fail, but on the other hand this is a FAQ on the list
        # ...
        del list_field.overrides['items']
        # test when TALES returns a list of e.g. int
        list_field.values['items'] = [('42', '42'), ('88', '88')]

        items1 = list_field.render()

        list_field.tales['items'] = TALESMethod("python:[42, 88]")
        items2 = list_field.render()

        self.assertEqual(items1, items2)

        list_field.validate({'field_list_field': '42'})

    def test_items_is_sequence(self):
        """ test that a multi list widget renders correctly,
        even if the items consist out of a tuple.
        this has bugged in some earlier version
        """
        # use a MultiCheckBoxField instead of a MultiListField just for
        # variance
        self.form.manage_addField(
            'list_field',
            'Test List Field',
            'MultiCheckBoxField')

        list_field = self.form.list_field
        list_field.values['items'] = [('foo', 'foo'), ('bar', 'bar')]

        items1 = list_field.render(('foo',))

        list_field.tales['items'] = TALESMethod("python:('foo', 'bar')")

        self.assertEqual(('foo', 'bar'), list_field.get_value('items'))

        items2 = list_field.render(('foo',))

        # test render
        self.assertEqual(items1, items2)
        # test render_view
        self.assertEqual("foo", list_field.render_view(('foo',)))

    def test_items_is_sequence_bis(self):
        """ test that a multi list values widget renders correctly,
            if the value from the request contains a list of non-ascii values
        """
        self.form.manage_addField(
            'list_boxes',
            'Test Checkboxes',
            'MultiCheckBoxField')
        self.encoding = "utf-8"
        self.form.unicode_mode = 1
        list_boxes = self.form.list_boxes
        list_boxes.values['unicode'] = 1
        list_boxes.values['items'] = \
            [(u'\xe4', u'A uml'), (u'\xfc', u'U uml')]
        request = TestRequest()
        request.form['key'] = [b'\xc3\xa4', b'\xc3\xbc']
        items = list_boxes._get_default(key='key', value=None,
                                        REQUEST=request)
        self.assertEqual([u'\xe4', u'\xfc'], items)

        # same with latin-1 (we should not hardcode utf-8)
        self.form.encoding = "latin-1"
        request.form['key'] = ['\xe4', '\xfc']
        items = list_boxes._get_default(key='key', value=None,
                                        REQUEST=request)
        self.assertEqual([u'\xe4', u'\xfc'], items)

    def test_lines_field_rendering(self):
        """ line fields should both accept lists / tuples
        of strings and single strings with whitespace.
        If they would not accept the second case, render_from_request
        would be broken.
        """
        self.form.manage_addField(
            'lines_field', 'Test Lines Field', 'LinesField')

        field = self.form.lines_field

        request = TestRequest()
        request.form['field_lines_field'] = 'Text'

        rendered = field.render(REQUEST=request)

        dom = parseString('<dummy>%s</dummy>' % rendered)
        divs = [child for child in dom.documentElement.childNodes
                if child.nodeType == child.ELEMENT_NODE]
        self.assertEqual(len(divs), 1)
        self.assertEqual(divs[0].nodeName, 'div')
        textareas = [child for child in divs[0].childNodes
                     if child.nodeType == child.ELEMENT_NODE]
        self.assertEqual(len(textareas), 1)
        self.assertEqual(textareas[0].nodeName, 'textarea')
        text = [child for child in textareas[0].childNodes
                if child.nodeType == child.TEXT_NODE]

        self.assertEqual('Text', ''.join([n.nodeValue for n in text]))

        field.values['hidden'] = 'checked'
        rendered = field.render(REQUEST=request)

    def test_labels(self):
        """ test that labels do not influence validation """
        self.form.manage_addField(
            'label_field', 'Test Label Field', 'LabelField')

        self.form.label_field.overrides['default'] = "Some label"

        self.form.manage_addField(
            'int_field', 'Test integer field', 'IntegerField')

        result = self.form.validate_all(
            {'field_int_field': '3'})
        self.assertEqual({'int_field': 3}, result)

    def test_labels_with_direct_validation(self):
        """ PloneFormMailer calls validate() directly on each field,
        this used to give a KeyError as 'external_validator' wasn't
        known for a label field.
        """
        self.form.manage_addField(
            'label_field', 'Test Label Field', 'LabelField')
        self.form['label_field'].validate(REQUEST=TestRequest())

    def test_datetime_css_class_rendering(self):
        # test that a bug is fixed, which causing the css_class value
        # not to be rendered for DateTime fields

        self.form.manage_addProduct['Formulator']\
                 .manage_addField('date_time', 'Test Field', 'DateTimeField')
        field = self.form.date_time

        css_matcher = re.compile('class="([^"]*)"')

        # initially no css class is set
        self.assertEqual(0, len(css_matcher.findall(field.render())))

        # edit the field, bypassing validation ...
        field._edit({'css_class': 'some_class'})

        # now we should have five matches for the five subfields ...
        css_matches = css_matcher.findall(field.render())
        self.assertEqual(10, len(css_matches))
        # ... and all have the given value:
        for m in css_matches:
            self.assertEqual('some_class', m)

        # change the input style: the css needs to be
        # propagated to the newly created subfields
        current_style = field['input_style']
        other_style = {'list': 'text', 'text': 'list'}[current_style]
        field._edit({'input_style': other_style})

        # still the css classes should remain the same
        css_matches = css_matcher.findall(field.render())
        self.assertEqual(7, len(css_matches))
        for m in css_matches:
            self.assertEqual('some_class', m)

        # now just change to another value:
        field._edit({'css_class': 'other_class'})
        css_matches = css_matcher.findall(field.render())
        self.assertEqual(7, len(css_matches))
        for m in css_matches:
            self.assertEqual('other_class', m)

        # and clear the css_class field:
        field._edit({'css_class': ''})
        css_matches = css_matcher.findall(field.render())
        self.assertEqual(0, len(css_matches))

    def _helper_render_datetime(
            self,
            expected_values,
            rendered,
            type='hidden'):
        # heper to check if the generated HTML from render or render_hidden
        # meets the expectations
        dom = parseString('<dummy>%s</dummy>' % rendered)
        elements = [child for child in dom.documentElement.childNodes
                    if child.nodeType == child.ELEMENT_NODE]
        if type != 'hidden':
            # They are wrapped in divs if not hidden
            self.assertEqual(len(elements), len(expected_values))
            inputs = []
            for element in elements:
                inputs.extend([child for child in element.childNodes
                               if child.nodeType == child.ELEMENT_NODE])
        else:
            inputs = elements

        self.assertEqual(len(list(expected_values.keys())), len(inputs))
        values = {}
        for input in inputs:
            self.assertEqual('input', input.nodeName)
            self.assertEqual(type, input.getAttribute('type'))
            self.assertFalse(input.childNodes)
            values[input.getAttribute('name')] = input.getAttribute('value')
        self.assertEqual(expected_values, values)

    def _helper_render_hidden_list(self, expected_name, expected_values,
                                   rendered):
        # heper to check if the generated HTML from render_hidden
        # meets the expectations
        dom = parseString('<dummy>%s</dummy>' % rendered)
        elements = [child for child in dom.documentElement.childNodes
                    if child.nodeType == child.ELEMENT_NODE]
        self.assertEqual(len(expected_values), len(elements))
        for child in elements:
            self.assertEqual('input', child.nodeName)
            self.assertEqual('hidden', child.getAttribute('type'))
            self.assertEqual(expected_name, child.getAttribute('name'))
            self.assertEqual(expected_values.pop(0),
                             child.getAttribute('value'))
            self.assertFalse(child.childNodes)

    def test_render_hidden(self):
        # test that rendering fields hidden does produce
        # meaningful results; i.e. such which may still lead to successful
        # validation when submitting a form with hidden fields
        # this has been broken for DateTimeFields, and fields
        # which allowed multiple values
        self.form.manage_addProduct['Formulator'].manage_addField(
            'date_time', 'Test Field', 'DateTimeField')
        self.form.manage_addProduct['Formulator'].manage_addField(
            'multi_list', 'Test Field', 'MultiListField')
        self.form.manage_addProduct['Formulator'].manage_addField(
            'check_boxes', 'Test Field', 'MultiCheckBoxField')
        self.form.manage_addProduct['Formulator'].manage_addField(
            'lines', 'Test Field', 'LinesField')

        self.form.date_time.values['default'] = DateTime(1970, 1, 1,)
        self.form.date_time.values['hidden'] = 1

        expected_values = {
            'subfield_date_time_year': '1970',
            'subfield_date_time_month': '01',
            'subfield_date_time_day': '01',
            'subfield_date_time_hour': '00',
            'subfield_date_time_minute': '00',
        }
        self._helper_render_datetime(expected_values,
                                     self.form.date_time.render())

        self.form.date_time.values['date_only'] = 1
        del expected_values['subfield_date_time_hour']
        del expected_values['subfield_date_time_minute']
        self._helper_render_datetime(expected_values,
                                     self.form.date_time.render())

        self.form.date_time.values['date_only'] = 0
        self.form.date_time.values['ampm_time_style'] = 1
        expected_values['subfield_date_time_hour'] = '12'
        expected_values['subfield_date_time_minute'] = '00'
        expected_values['subfield_date_time_ampm'] = 'am'
        self._helper_render_datetime(expected_values,
                                     self.form.date_time.render())

        self.form.multi_list.values['items'] = (
            ('a', 'a'), ('b', 'b'), ('c', 'c'))
        self.form.multi_list.values['default'] = ['a', 'c']
        self.form.multi_list.values['hidden'] = 1
        self._helper_render_hidden_list('field_multi_list', ['a', 'c'],
                                        self.form.multi_list.render())

        self.form.check_boxes.values['items'] = (
            ('a', 'a'), ('b', 'b'), ('c', 'c'))
        self.form.check_boxes.values['default'] = ['a', 'c']
        self.form.check_boxes.values['hidden'] = 1
        self._helper_render_hidden_list('field_check_boxes', ['a', 'c'],
                                        self.form.check_boxes.render())

        self.form.lines.values['default'] = ['a', 'c']
        self.form.lines.values['hidden'] = 1
        expect_str = 'a\nc'
        # FIXME: a straight comparision fails ...
        # minidom seems to barf on string linebreaks in attributes (?)
        # instead ...
        rendered = self.form.lines.render()
        rendered = rendered.replace('\n', 'NEWLINE_HERE')
        expect_str = expect_str.replace('\n', 'NEWLINE_HERE')
        self._helper_render_hidden_list('field_lines', [expect_str],
                                        rendered)

    def test_render_view_items(self):
        # test that the render_view is correct for fields
        # for which the values internally handled by Formulator
        # are different from the ones shown to the user
        # (e.g. checkboxes, radio buttons, option-lists)

        self.form.manage_addProduct['Formulator']\
            .manage_addField('single_list', 'Test Field', 'ListField')
        self.form.manage_addProduct['Formulator']\
            .manage_addField('multi_list', 'Test Field', 'MultiListField')
        self.form.manage_addProduct['Formulator']\
                 .manage_addField('check_boxes', 'Test Field',
                                  'MultiCheckBoxField')
        self.form.manage_addProduct['Formulator']\
                 .manage_addField('radio', 'Test Field', 'RadioField')

        for field in self.form.single_list, self.form.radio:
            field.values['items'] = [('Alpha', 'a'),
                                     ('Beta', 'b'),
                                     ('Gamma', 'c'), ]
            self.assertEqual('Gamma', field.render_view('c'), msg=field.id)

        for field in self.form.multi_list, self.form.check_boxes:
            field.values['items'] = [('Alpha', 'a'),
                                     ('Beta', 'b'),
                                     ('Gamma', 'c'), ]

            field.values['view_separator'] = '|||'
            self.assertEqual('Gamma', field.render_view(['c']))
            self.assertEqual('|||'.join(('Alpha', 'Gamma')),
                             field.render_view(['a', 'c']))
            self.assertEqual('', field.render_view([]))

    def test_default_to_now_does_not_overwrite_request_values(self):
        self.form.manage_addField(
            'date_field',
            'Test DateTime Field',
            'DateTimeField')
        date_field = self.form.date_field

        date_field.values['default_now'] = 1
        date_field.values['default'] = DateTime('1971/01/01')
        date_field.values['date_only'] = 1  # for less typing in test only ...

        expected_values = \
            {'subfield_date_field_year': '1970',
             'subfield_date_field_month': '01',
             'subfield_date_field_day': '01'}

        request = TestRequest(form=expected_values)
        rendered = date_field.render_from_request(request)
        self._helper_render_datetime(expected_values, rendered, type='text')

        # as we are already here, check yet another thing:
        # test that default is honored if no value given
        expected_values['subfield_date_field_year'] = '1971'
        rendered = date_field.render_from_request(TestRequest())
        self._helper_render_datetime(expected_values, rendered, type='text')

    def test_checkbox_default_overwrites_submitted_values(self):
        self.form.manage_addField(
            'checkbox_field',
            'Test Checkbox',
            'CheckBoxField')
        checkbox_field = self.form.checkbox_field

        checkbox_field.values['default'] = 1

        rendered = checkbox_field.render()
        self.assertNotEqual(-1, rendered.find('checked="checked"'))

        request = TestRequest()
        rendered = checkbox_field.render_from_request(request)
        self.assertNotEqual(-1, rendered.find('checked="checked"'))

        request.form['formulator_submission'] = '1'
        rendered = checkbox_field.render_from_request(request)
        self.assertEqual(-1, rendered.find('checked="checked"'))

    def test_edit_listitem(self):
        """ if eding a list item via ZMI (or xml rpc) in unicode mode
        this has blown because some lists of strings have
        not been converted properly
        """
        self.form.unicode_mode = 1
        self.form.manage_addField('list_field', 'Test Listfield', 'ListField')
        self.form.manage_addField(
            'lines_field',
            'Test Linesfield',
            'LinesField')
        list_field = self.form.list_field
        lines_field = self.form.lines_field
        # just to make sure
        self.assertTrue(list_field.get_unicode_mode())

        # the list field has the most complicated setting:
        # a list of 2-tuples for the 'items'
        request = TestRequest(form={
            'field_title': b'Title\xc3\xbc',
            'field_default': b'item\xc3\xbc',
            'field_items': b'item\xc3\xbc | item_ue\nitem2 | item2',
            'field_size': '7',
        })
        list_field.manage_edit(request)
        self.assertEqual(u'item\xfc',
                         list_field.get_value('default'))
        expected_items = [(u'item\xfc', u'item_ue'), ('item2', 'item2')]
        self.assertEqual(expected_items,
                         list_field.get_value('items'))

        self.assertEqual(7, list_field.get_value('size'))

        # the lines field has a plain list of string as 'default'
        request = TestRequest(form={
            'field_title': b'Title\xc3\xbc',
            'field_default': b'item\xc3\xbc\nitem2',
            'field_width': '40',
            'field_height': '5',
            'field_view_separator': b'sep \xc3\xbc',
        })
        lines_field.manage_edit(request)
        self.assertEqual(u'Title\xfc',
                         lines_field.get_value('title'))
        self.assertEqual([u'item\xfc', u'item2'],
                         lines_field.get_value('default'))

    def test_tales_none(self):
        # test that a TALES default of None is rendered
        # as the empty string in the field's value attribute
        # and not as "value"
        self.form.manage_addField('text', 'Text Field', 'StringField')
        text = self.form.text
        text.tales['default'] = TALESMethod('nothing')
        self.assertEqual(1, text.render().count('value=""'))

    def test_add_unicode_form(self):
        # test bugfix when adding a form with a non-ascii title
        # and the unicode flag set
        self.root.manage_addProduct['Formulator'].manage_add(
            'form2', b'Test Form b\xef\xbf\xbdr', unicode_mode=1)
        form2 = self.root.form2
        self.assertEqual(1, form2.get_unicode_mode())
        self.assertEqual(type(u' '), type(form2.title))
        self.assertEqual(u'Test Form b\ufffdr', form2.title)

    def test_add_unicode_field(self):
        # test bugfix when adding a field with a non-ascii title
        # to a form with the unicode flag set
        self.root.manage_addProduct['Formulator'].manage_add(
            'form2', 'Test Form b\xef\xbf\xbdr', unicode_mode=1)
        form2 = self.root.form2
        self.assertEqual(1, form2.get_unicode_mode())

        form2.manage_addField('testfield', b'Test field b\xef\xbf\xbdr',
                              'StringField')
        self.assertEqual(type(u' '), type(form2.testfield.title()))
        self.assertEqual(u'Test field b\ufffdr', form2.testfield.title())
        self.assertEqual(
            u'Test field b\ufffdr',
            form2.testfield.get_value('title'))

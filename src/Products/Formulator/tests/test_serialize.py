# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

import re
import unittest

import six

from DateTime import DateTime

from Products.Formulator.Errors import FormValidationError
from Products.Formulator.Errors import ValidationError
from Products.Formulator.Form import ZMIForm
from Products.Formulator.FormToXML import formToXML
from Products.Formulator.MethodField import Method
from Products.Formulator.testing import FunctionalLayer
from Products.Formulator.testing import TestRequest
from Products.Formulator.XMLToForm import XMLToForm


class SerializeTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.layer.login('manager')
        self.root = self.layer.get_application()

    def test_simpleSerialize(self):
        form = ZMIForm('test', 'My test')
        xml = '''\
<?xml version="1.0" encoding="iso-8859-1" ?>

<form>
  <title></title>
  <name>tab_status_form</name>
  <action></action>
  <enctype></enctype>
  <method></method>

  <groups>
    <group>
      <title>Default</title>
      <fields>

      <field><id>message</id> <type>RawTextAreaField</type>
        <values>
          <alternate_name></alternate_name>
          <hidden type="int">0</hidden>
          <max_length></max_length>
          <width type="int">65</width>
          <external_validator></external_validator>
          <height type="int">7</height>
          <required type="int">0</required>
          <css_class></css_class>
          <default></default>
          <title>Message</title>
          <truncate type="int">0</truncate>
          <description></description>
          <extra>wrap="soft"</extra>
        </values>
        <tales>
        </tales>
      </field>
      <field><id>publish_datetime</id> <type>DateTimeField</type>
        <values>
          <date_only type="int">0</date_only>
          <alternate_name></alternate_name>
          <input_style>list</input_style>
          <hidden type="int">0</hidden>
          <input_order>dmy</input_order>
          <time_separator>:</time_separator>
          <date_separator>/</date_separator>
          <external_validator></external_validator>
          <required type="int">0</required>
          <default_now type="int">0</default_now>
          <css_class></css_class>
          <title>Publish time</title>
          <description></description>
        </values>
        <tales>
          <time_separator>python:form.time_punctuation</time_separator>
          <date_separator>python:form.date_punctuation</date_separator>
        </tales>
      </field>
      <field><id>expiration_datetime</id> <type>DateTimeField</type>
        <values>
          <date_only type="int">0</date_only>
          <alternate_name></alternate_name>
          <input_style>list</input_style>
          <css_class></css_class>
          <hidden type="int">0</hidden>
          <input_order>dmy</input_order>
          <time_separator>:</time_separator>
          <date_separator>/</date_separator>
          <external_validator></external_validator>
          <required type="int">0</required>
          <default_now type="int">0</default_now>
          <title>Expiration time</title>
          <description>If this document should expire, set the time.</description>
        </values>
        <tales>
          <time_separator>python:form.time_punctuation</time_separator>
          <date_separator>python:form.date_punctuation</date_separator>
        </tales>
      </field>
      <field><id>expires_flag</id> <type>CheckBoxField</type>
        <values>
          <alternate_name></alternate_name>
          <hidden type="int">0</hidden>
          <css_class></css_class>
          <default type="int">0</default>
          <title>Expire flag</title>
          <description>Turn on expiration time?</description>
          <external_validator></external_validator>
          <extra></extra>
        </values>
        <tales>
        </tales>
      </field>
      </fields>
    </group>
  </groups>
</form>'''  # noqa: E501 line too long
        XMLToForm(xml, form)
        b = formToXML(form)
        f = open('output1.txt', 'w')
        f.write(b)
        f.close()
        form2 = ZMIForm('another', 'Something')
        XMLToForm(xml, form2)
        f = open('output2.txt', 'w')
        f.write(formToXML(form2))
        f.close()

    def assertEqualForms(self, form1, form2):
        """ test that the two forms are equal (except for their ids) """
        # in case of failures the messages could be nicer ...

        self.assertEqual([x.getId() for x in form1.get_fields()],
                         [x.getId() for x in form2.get_fields()])
        for field in form1.get_fields():
            self.assertTrue(form2.has_field(field.getId()))
            field2 = getattr(form2, field.getId())
            # test if values are the same
            self.assertEqual(field.values, field2.values)
            # test if default renderings are the same
            self.assertEqual(field.render(), field2.render())

        self.assertEqual(form1.title, form2.title)
        # self.assertEqual(form1.row_lenght, form2.row_lenght) # not
        # initialized ?
        self.assertEqual(form1.name, form2.name)
        self.assertEqual(form1.action, form2.action)
        self.assertEqual(form1.method, form2.method)
        self.assertEqual(form1.enctype, form2.enctype)
        self.assertEqual(form1.encoding, form2.encoding)
        self.assertEqual(form1.stored_encoding, form2.stored_encoding)
        self.assertEqual(form1.unicode_mode, form2.unicode_mode)
        self.assertEqual(form1.i18n_domain, form2.i18n_domain)

        self.assertEqual(form1.get_groups(), form2.get_groups())

        # if we have forgotten something, this will usually remind us ;-)
        self.assertEqual(form1.render(), form2.render())

    def test_escaping(self):
        """ test if the necessary elements are escaped in the XML.
        (Actually this test is very incomplete)
        """
        form = ZMIForm('test', '<EncodingTest>')
        # XXX don't test escaping of name, as needs to be javascript
        # valid anyway?
        form.name = 'name'
        form.add_group('a & b')

        form.manage_addField('string_field', '<string> Field', 'StringField')
        form.manage_addField('int_field', '<int> Field', 'IntegerField')
        form.manage_addField('float_field', '<Float> Field', 'FloatField')
        form.manage_addField('date_field', '<Date> Field', 'DateTimeField')
        form.manage_addField('list_field', '<List> Field', 'ListField')
        form.manage_addField(
            'multi_field',
            '<Checkbox> Field',
            'MultiCheckBoxField')

        form2 = ZMIForm('test2', 'ValueTest')

        xml = formToXML(form)
        XMLToForm(xml, form2)

        self.assertEqualForms(form, form2)

    def test_messages(self):
        """ test if the error messages are exported
        """
        factory = self.root.manage_addProduct['Formulator']
        factory.manage_add('form', 'Test Form')
        form = self.root.form
        form.manage_addField('int_field', 'int Field', 'IntegerField')

        form2 = ZMIForm('test2', 'ValueTest')
        request = TestRequest()
        for message_key in form.int_field.get_error_names():
            request.form[message_key] = (
                'test message for error key <%s>' % message_key)
        form.int_field.manage_messages(REQUEST=request)

        xml = formToXML(form)
        XMLToForm(xml, form2)
        # print xml

        request = TestRequest(form={'field_int_field': 'not a number'})
        try:
            form.validate_all(request)
            self.fail('form should fail in validation')
        except FormValidationError as e:
            self.assertEqual(1, len(e.errors))
            text1 = e.errors[0].error_text

        try:
            form2.validate_all(request)
            self.fail('form2 should fail in validation')
        except FormValidationError as e:
            self.assertEqual(1, len(e.errors))
            text2 = e.errors[0].error_text

        self.assertEqual(six.text_type(text1), six.text_type(text2))

    def test_fieldValueTypes(self):
        """ test checking if the field values are of the proper type.
        after reading from XML some field values may not have the right type,
        if they have a special type (only for "int" and "list" yet).
        Also tests if rendering and validation are the same
        between the original form and the one after one form -> xml -> form
        roundtrip.
        """
        # tests for "method" and "datetime" values follow later on ...
        # booleans are not tested yet

        factory = self.root.manage_addProduct['Formulator']
        factory.manage_add('form', 'ValueTest')
        factory.manage_add('form2', 'ValueTest')
        form = self.root.form
        form.manage_addField('int_field', 'Test Integer Field', 'IntegerField')
        form.manage_addField('float_field', 'Test Float Field', 'FloatField')
        form.manage_addField('date_field', 'Test Date Field', 'DateTimeField')
        form.manage_addField('list_field', 'Test List Field', 'ListField')
        form.manage_addField(
            'multi_field',
            'Test Checkbox Field',
            'MultiCheckBoxField')
        form.manage_addField('link_field', 'Test Link Field', 'LinkField')
        form.manage_addField('empty_field', 'Test Empty Field', 'StringField')
        int_field = form.int_field
        float_field = form.float_field
        date_field = form.date_field
        list_field = form.list_field
        multi_field = form.multi_field
        link_field = form.link_field
        empty_field = form.empty_field

        # XXX editing fields by messing with a fake request
        # -- any better way to do this?
        # (could assign to "values" directly ...)

        default_values = {'field_title': 'Test Title',
                          'field_display_width': '92',
                          'field_required': 'checked',
                          'field_enabled': 'checked',
                          }
        try:
            form_values = default_values.copy()
            form_values.update({'field_default': 'None',
                                'field_required': '',
                                })
            empty_field.manage_edit(REQUEST=TestRequest(form=form_values))

            form_values = default_values.copy()
            form_values.update({'field_default': '42',
                                'field_enabled': 'checked'})
            int_field.manage_edit(REQUEST=TestRequest(form=form_values))

            form_values = default_values.copy()
            form_values.update({'field_default': '1.7'})
            float_field.manage_edit(REQUEST=TestRequest(form=form_values))

            # XXX cannot test "defaults to now", as this may fail randomly
            form_values = default_values.copy()
            form_values.update({'field_input_style': 'list',
                                'field_input_order': 'mdy',
                                'field_date_only': '',
                                'field_css_class': 'test_css',
                                'field_time_separator': '$'})
            date_field.manage_edit(REQUEST=TestRequest(form=form_values))

            form_values = default_values.copy()
            form_values.update({'field_default': 'foo',
                                'field_size': '1',
                                'field_items': 'Foo | foo\n Bar | bar'})
            list_field.manage_edit(REQUEST=TestRequest(form=form_values))

            form_values = default_values.copy()
            form_values.update(
                {'field_default': 'foo',
                 'field_size': '3',
                 'field_items': 'Foo | foo\n Bar | bar\nBaz | baz',
                 'field_orientation': 'horizontal',
                 'field_view_separator': '<br />\n'})
            multi_field.manage_edit(REQUEST=TestRequest(form=form_values))

            form_values = default_values.copy()
            form_values.update({'field_default': 'http://www.absurd.org',
                                'field_required': '1',
                                'field_check_timeout': '5.0',
                                'field_link_type': 'external',
                                })
            link_field.manage_edit(REQUEST=TestRequest(form=form_values))

        except ValidationError as e:
            self.fail('error when editing field %s; error message: %s' %
                      (e.field_id, e.error_text))

        form2 = self.root.form2

        xml = formToXML(form)
        XMLToForm(xml, form2)

        self.assertEqualForms(form, form2)

        request = TestRequest()
        request.form['field_int_field'] = '42'
        request.form['field_float_field'] = '2.71828'
        request.form['subfield_date_field_month'] = '11'
        request.form['subfield_date_field_day'] = '11'
        # This field only allows ten years in the future, today 2023-03-14
        request.form['subfield_date_field_year'] = '2033'
        request.form['subfield_date_field_hour'] = '09'
        request.form['subfield_date_field_minute'] = '59'
        request.form['field_list_field'] = 'bar'
        request.form['field_multi_field'] = ['bar', 'baz']
        request.form['field_link_field'] = 'http://www.zope.org'
        try:
            result1 = form.validate_all(request)
        except FormValidationError as e:
            # XXX only render first error ...
            self.fail('error when editing form1, field %s; error message: %s' %
                      (e.errors[0].field_id, e.errors[0].error_text))

        try:
            result2 = form2.validate_all(request)
        except FormValidationError as e:
            # XXX only render first error ...
            self.fail('error when editing form1, field %s; error message: %s' %
                      (e.errors[0].field_id, e.errors[0].error_text))
        self.assertEqual(result1, result2)
        self.assertEqual(42, result2['int_field'])
        self.assertEqual(2.71828, result2['float_field'])

        # check link field timeout value
        self.assertEqual(link_field.get_value('check_timeout'),
                         form2.link_field.get_value('check_timeout'))

        # XXX not tested: equal form validation failure on invalid input

    def test_emptyGroup(self):
        """ test bugfix: empty groups are allowed in the XMLForm """
        form = ZMIForm('test', 'GroupTest')
        form.add_group('empty')

        form2 = ZMIForm('test2', 'GroupTestCopy')

        xml = formToXML(form)
        XMLToForm(xml, form2)
        # print xml
        self.assertEqualForms(form, form2)

    def test_validatorMethod(self):
        self.root.manage_addProduct['Formulator'] \
            .manage_add('form', 'Test Form')
        form = self.root.form

        self.root.manage_addDTMLMethod('test_dtml', 'Test DTML', 'ok')

        form.manage_addField('string_field', '<string> Field', 'StringField')
        form.string_field.values['external_validator'] = Method('test_dtml')

        # test that the override works:
        self.assertEqual('ok',
                         form.string_field.get_value('external_validator')())

        # now serialize it:
        xml = formToXML(form)

        # get the external validator from the output
        # XXX this could be more elegant, I guess ...
        if six.PY2:
            xml_decoded = xml.decode('utf-8')
        else:
            xml_decoded = xml
        for line in xml_decoded.split('\n'):
            m = re.match(
                r'\s*<external_validator type="method">(.*?)'
                r'</external_validator>\s*',
                line)
            if m:
                break
        else:
            self.fail('external_validator not found in xml')
        self.assertEqual('test_dtml', m.group(1))

        # deserialize it
        self.root.manage_addProduct['Formulator'] \
            .manage_add('form2', 'Test Form')
        form2 = self.root.form2
        XMLToForm(xml, form2)
        self.assertEqual('ok',
                         form2.string_field.get_value('external_validator')())

    def test_serializeDateTimeValues(self):
        form = ZMIForm('test', 'DateTime')

        form.manage_addField('date_field', 'Date Field', 'DateTimeField')
        form.date_field.values['start_datetime'] = DateTime(
            '2004/01/01 12:01:00')

        form2 = ZMIForm('test', 'DateTime2')

        xml = formToXML(form)
        XMLToForm(xml, form2)

        self.assertEqualForms(form, form2)

    def test_deserializeFlushesOldFields(self):
        # test that deserializing a form removes old values which
        # have been defined on that from previously
        # this may be an issue if one edits a form directly
        # via the ZMI "XML" tab; removing a field in the XML did not
        # remove that field from the form contents
        form = ZMIForm('test', 'Source')
        form2 = ZMIForm('test2', 'Target')

        form.manage_addField('date_field', 'Date Field', 'DateTimeField')
        form2.manage_addField('another_field', 'String Field', 'StringField')

        xml = formToXML(form)
        XMLToForm(xml, form2)

        self.assertEqualForms(form, form2)
        self.assertFalse(form2.has_field('another_field'))
        self.assertNotIn('another_field', form2.objectIds())

    def test_serializeDeserializeEncodedMessages(self):
        # test for serializing and deserializing XML with non-ascii text in
        # the message tags
        xml1 = """\
<?xml version="1.0"?>

<form>
  <title></title>
  <row_length>4</row_length>
  <name>testform_bugs</name>
  <action></action>
  <method>POST</method>
  <enctype></enctype>
  <encoding>UTF-8</encoding>
  <stored_encoding>UTF-8</stored_encoding>
  <unicode_mode>false</unicode_mode>
  <i18n_domain></i18n_domain>
  <groups>
    <group>
      <title>Default</title>
      <fields>

      <field><id>string</id> <type>StringField</type>
        <values>
          <alternate_name></alternate_name>
          <css_class></css_class>
          <default></default>
          <description>मैं काँच खा सकता हूँ, मुझे उस से कोई पीडा</description>
          <display_maxwidth></display_maxwidth>
          <display_width type="int">20</display_width>
          <enabled type="int">1</enabled>
          <external_validator></external_validator>
          <extra></extra>
          <hidden type="int">0</hidden>
          <max_length></max_length>
          <required type="int">1</required>
          <title>मैं काँच खा सकता हूँ, मुझे उस से कोई पीडा</title>
          <truncate type="int">0</truncate>
          <unicode type="int">0</unicode>
          <whitespace_preserve type="int">0</whitespace_preserve>
        </values>
        <tales>
        </tales>
        <messages>
          <message name="external_validator_failed">मैं काँच खा सकता हूँ, मुझे उस से कोई पीडा</message>
          <message name="required_not_found">मैं काँच खा सकता हूँ, मुझे उस से कोई पीडा</message>
          <message name="too_long">मैं काँच खा सकता हूँ, मुझे उस से कोई पीडा</message>
        </messages>
      </field>
      </fields>
    </group>
  </groups>
</form>
"""  # noqa: E501 line too long

        # we're not expecting exceptions, and don't really care about anything
        # else, so no asserts here...
        form = ZMIForm('foo', 'Foo')
        XMLToForm(xml1, form)
        formToXML(form)

        xml1 = """\
<?xml version="1.0"?>

<form>
  <title></title>
  <row_length>4</row_length>
  <name>testform_bugs</name>
  <action></action>
  <method>POST</method>
  <enctype></enctype>
  <encoding>UTF-8</encoding>
  <stored_encoding>UTF-8</stored_encoding>
  <unicode_mode>true</unicode_mode>
  <i18n_domain></i18n_domain>
  <groups>
    <group>
      <title>Default</title>
      <fields>

      <field><id>string</id> <type>StringField</type>
        <values>
          <alternate_name></alternate_name>
          <css_class></css_class>
          <default></default>
          <description>मैं काँच खा सकता हूँ, मुझे उस से कोई पीडा</description>
          <display_maxwidth></display_maxwidth>
          <display_width type="int">20</display_width>
          <enabled type="int">1</enabled>
          <external_validator></external_validator>
          <extra></extra>
          <hidden type="int">0</hidden>
          <max_length></max_length>
          <required type="int">1</required>
          <title>मैं काँच खा सकता हूँ, मुझे उस से कोई पीडा</title>
          <truncate type="int">0</truncate>
          <unicode type="int">0</unicode>
          <whitespace_preserve type="int">0</whitespace_preserve>
        </values>
        <tales>
        </tales>
        <messages>
          <message name="external_validator_failed">मैं काँच खा सकता हूँ, मुझे उस से कोई पीडा</message>
          <message name="required_not_found">मैं काँच खा सकता हूँ, मुझे उस से कोई पीडा</message>
          <message name="too_long">मैं काँच खा सकता हूँ, मुझे उस से कोई पीडा</message>
        </messages>
      </field>
      </fields>
    </group>
  </groups>
</form>
"""  # noqa: E501 line too long

        # we're not expecting exceptions, and don't really care about anything
        # else, so no asserts here...
        form = ZMIForm('foo', 'Foo')
        XMLToForm(xml1, form)
        formToXML(form)

# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

import six
from six.moves import range

from AccessControl.tainted import TaintedString
from DateTime import DateTime

from Products.Formulator import Validator
from Products.Formulator.StandardFields import DateTimeField
from Products.Formulator.testing import FunctionalLayer


class TestField:
    def __init__(self, id, **kw):
        self.id = id
        self.kw = kw

    def get_value(self, name):
        # XXX hack
        return self.kw.get(name, 0)

    def get_error_message(self, key):
        return "nothing"

    def get_form_encoding(self):
        # XXX fake ... what if installed python does not support utf-8?
        return "utf-8"


class FakeSaxHandler:
    def __init__(self):
        self._xml = ''

    def startElement(self, key):
        self._xml = self._xml + '<%s>' % key

    def endElement(self, key):
        self._xml = self._xml + '</%s>' % key

    def characters(self, characters):
        self._xml = self._xml + characters

    def getXml(self):
        return self._xml


class ValidatorTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def assertValidatorRaises(self, exception, error_key, f, *args, **kw):
        try:
            f(*args, **kw)
        except Validator.ValidationError as e:
            if e.error_key != error_key:
                self.fail('Got wrong error. Expected %s received %s' %
                          (error_key, e))
            else:
                return
        self.fail('Expected error %s but no error received.' % error_key)


class StringValidatorTestCase(ValidatorTestCase):

    def setUp(self):
        self.v = Validator.StringValidatorInstance

    def test_basic(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0),
            'f', {'f': 'foo'})
        self.assertEqual('foo', result)

    def test_htmlquotes(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0),
            'f', {'f': '<html>'})
        self.assertEqual('<html>', result)

    def test_encoding(self):
        utf8_string = b'M\303\274ller'  # this is a M&uuml;ller
        unicode_string = six.text_type(utf8_string, 'utf-8')
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=1),
            'f', {'f': utf8_string})
        self.assertEqual(unicode_string, result)

    def test_strip_whitespace(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0),
            'f', {'f': ' foo  '})
        self.assertEqual('foo', result)

    def test_error_too_long(self):
        self.assertValidatorRaises(
            Validator.ValidationError, 'too_long',
            self.v.validate,
            TestField('f', max_length=10, truncate=0, required=0, unicode=0),
            'f', {'f': 'this is way too long'})

    def test_error_truncate(self):
        result = self.v.validate(
            TestField('f', max_length=10, truncate=1, required=0, unicode=0),
            'f', {'f': 'this is way too long'})
        self.assertEqual('this is way too long'[:10], result)

    def test_error_required_not_found(self):
        # empty string
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': ''})
        # whitespace only
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': '   '})
        # not in dict
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {})

    def test_whitespace_preserve(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0,
                      whitespace_preserve=1),
            'f', {'f': ' '})
        self.assertEqual(' ', result)

        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0,
                      whitespace_preserve=0),
            'f', {'f': ' '})
        self.assertEqual('', result)

        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0,
                      whitespace_preserve=1),
            'f', {'f': ' foo '})
        self.assertEqual(' foo ', result)

    def test_brokenTaintedString(self):
        # same as test_basic, instead that we pass in a "TaintedString"
        # this in passed by ZPublisher and looks like a string most of the time
        # but has been broken wrt. to the string.strip module in conjunction
        # with python 2.3.x. Check that we do not run into this brokeness
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0),
            'f', {'f': TaintedString('<foo>')})
        self.assertEqual('<foo>', result)

    def test_serializeValue(self):
        handler = FakeSaxHandler()
        string = 'This is the string value'
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1)
        self.v.serializeValue(field, string, handler)
        self.assertEqual('This is the string value', handler.getXml())

    def test_deserializeValue(self):
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1)
        self.assertEqual(
            'This is the string value',
            self.v.deserializeValue(field, 'This is the string value'))

    def test_serializeNonStringValues(self):
        not_a_string = 0
        handler = FakeSaxHandler()
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1)
        self.v.serializeValue(field, not_a_string, handler)
        self.assertEqual('0', handler.getXml())


class LinesValidatorTestVase(ValidatorTestCase):

    def setUp(self):
        self.v = Validator.LinesValidatorInstance

    def test_whitespace_preserve(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': 'Two Lines \n of Text'})
        self.assertEqual(['Two Lines', 'of Text'], result)
        # without stripping whitespace
        result = self.v.validate(
            TestField('f', max_lenght=0, whitespace_preserve=1,
                      truncate=0, required=1, unicode=0),
            'f', {'f': 'Two Lines \n of Text'})
        self.assertEqual(['Two Lines ', ' of Text'], result)

    def test_maxlength(self):
        # currently the validator checks the max lenght before
        # stripping whitespace from each line (and includes the
        # linebreaks)
        self.assertValidatorRaises(
            Validator.ValidationError, 'too_long',
            self.v.validate,
            TestField('f', max_length=12, truncate=0, required=1, unicode=0),
            'f', {'f': 'Too long\n text'})
        # empty lines in the middle count for "max_lines"
        self.assertValidatorRaises(
            Validator.ValidationError, 'too_many_lines',
            self.v.validate,
            TestField('f', max_lines=2, truncate=0, required=1, unicode=0),
            'f', {'f': 'Too long\n\n text'})
        # when stripping whitespace, only leading \n will be stripped
        self.v.validate(
            TestField('f', max_lines=2, truncate=0, required=1, unicode=0),
            'f', {'f': '\nToo long\n text'})
        # without stripping whitespace not even these will ne stripped
        self.assertValidatorRaises(
            Validator.ValidationError, 'too_many_lines',
            self.v.validate,
            TestField('f', max_lines=2, whitespace_preserve=1,
                      truncate=0, required=1, unicode=0),
            'f', {'f': 'A really\ntoo long\n text'})
        # check max_linelength works
        self.assertValidatorRaises(
            Validator.ValidationError, 'line_too_long',
            self.v.validate,
            TestField('f', max_linelength=8, whitespace_preserve=1,
                      truncate=0, required=1, unicode=0),
            'f', {'f': '\nToo long \ntext'})

    def test_serializeValue(self):
        handler = FakeSaxHandler()
        value = ['Two Lines ', ' of Text']
        field = TestField(
            'f', max_length=0, truncate=0, required=1, unicode=0)
        self.v.serializeValue(field, value, handler)
        self.assertEqual('Two Lines \n of Text', handler.getXml())

    def test_deserializeValue(self):
        string = 'Two Lines \n of Text'
        field = TestField(
            'f',
            max_length=0,
            truncate=0,
            whitespace_preserve=1,
            required=0,
            unicode=1)
        self.assertEqual(
            ['Two Lines ', ' of Text'],
            self.v.deserializeValue(field, string))


class SelectionValidatorTestCase(ValidatorTestCase):

    def setUp(self):
        self.v = Validator.SelectionValidatorInstance

    def test_items(self):
        result = self.v.validate(
            TestField(
                'f', required=1, unicode=True, items=[
                    ('Some A here', 'a'), ('Some B then', 'b')]),
            'f', {'f': 'b'})
        self.assertEqual('b', result)
        # With single items
        result = self.v.validate(
            TestField('f', required=1, unicode=True, items=[('ab', 'bb')]),
            'f', {'f': 'bb'})
        self.assertEqual('bb', result)
        # Empty
        result = self.v.validate(
            TestField(
                'f', required=0, unicode=True, items=[
                    ('Some A here', 'a'), ('Some B then', 'b')]),
            'f', {})
        self.assertEqual(u'', result)

    def test_integer_items(self):
        result = self.v.validate(
            TestField(
                'f', required=1, unicode=True, items=[
                    ('Un', 1), ('Deux', 2)]),
            'f', {'f': '1'})
        self.assertEqual(1, result)

    def test_unicode_items(self):
        result = self.v.validate(
            TestField(
                'f', required=1, unicode=True, items=[
                    (u'Some \xc3\x84 here', u'\xe4'), (u'Some B then', u'b')]),
            'f', {'f': b'\xc3\xa4'})
        self.assertEqual(u'\xe4', result)

    def test_invalid_items(self):
        with self.assertRaises(Validator.ValidationError) as error:
            self.v.validate(
                TestField(
                    'f', required=1, unicode=True, items=[
                        ('Some A here', 'a'), ('Some B then', 'b')]),
                'f', {'f': 'c'})
        self.assertEqual('unknown_selection', error.exception.error_key)


class MultiSelectionValidatorTestCase(ValidatorTestCase):

    def setUp(self):
        self.v = Validator.MultiSelectionValidatorInstance

    def test_items(self):
        result = self.v.validate(
            TestField(
                'f', required=1, unicode=True, items=[
                    ('Some A here', 'a'), ('Some B then', 'b')]),
            'f', {'f': 'b'})
        self.assertEqual(['b'], result)
        # Empty
        result = self.v.validate(
            TestField(
                'f', required=0, unicode=True, items=[
                    ('Some A here', 'a'), ('Some B then', 'b')]),
            'f', {})
        self.assertEqual([], result)

    def test_unicode_items(self):
        result = self.v.validate(
            TestField(
                'f', required=1, unicode=True, items=[
                    (u'Some \xc3\x84 here', u'\xe4'), (u'Some B then', u'b')]),
            'f', {'f': b'\xc3\xa4'})
        self.assertEqual([u'\xe4'], result)

    def test_invalid_items(self):
        with self.assertRaises(Validator.ValidationError) as error:
            self.v.validate(
                TestField(
                    'f', required=1, unicode=True, items=[
                        ('Some A here', 'a'), ('Some B then', 'b')]),
                'f', {'f': ['a', 'c']})
        self.assertEqual('unknown_selection', error.exception.error_key)


class EmailValidatorTestCase(ValidatorTestCase):

    def setUp(self):
        self.v = Validator.EmailValidatorInstance

    def test_basic(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': 'foo@bar.com'})
        self.assertEqual('foo@bar.com', result)
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': 'm.faassen@vet.uu.nl'})
        self.assertEqual('m.faassen@vet.uu.nl', result)

    def test_error_not_email(self):
        # a few wrong email addresses should raise error
        self.assertValidatorRaises(
            Validator.ValidationError, 'not_email',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': 'foo@bar.com.'})
        self.assertValidatorRaises(
            Validator.ValidationError, 'not_email',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': '@bar.com'})

    def test_error_required_not_found(self):
        # empty string
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': ''})

    def test_serializeValue(self):
        handler = FakeSaxHandler()
        string = 'eric@infrae.com'
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1)
        self.v.serializeValue(field, string, handler)
        self.assertEqual('eric@infrae.com', handler.getXml())

    def test_deserializeValue(self):
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1)
        self.assertEqual(
            'eric@infrae.com',
            self.v.deserializeValue(field, 'eric@infrae.com'))


class PatternValidatorTestCase(ValidatorTestCase):

    def setUp(self):
        self.v = Validator.PatternValidatorInstance

    def test_ff_pattern(self):
        # test bug where an 'd','e' or 'f' in the input
        # caused garbled output for some patterns
        pattern = 'f-f'
        value = 'd-1'

        field = \
            TestField('f', max_length=0, truncate=0, required=1, unicode=0,
                      pattern=pattern)
        result = self.v.validate(field, 'f', {'f': value})
        self.assertEqual(value, result)


class BooleanValidatorTestCase(ValidatorTestCase):

    def setUp(self):
        self.v = Validator.BooleanValidatorInstance

    def test_basic(self):
        result = self.v.validate(
            TestField('f'),
            'f', {'f': ''})
        self.assertEqual(0, result)
        result = self.v.validate(
            TestField('f'),
            'f', {'f': 1})
        self.assertEqual(1, result)
        result = self.v.validate(
            TestField('f'),
            'f', {'f': 0})
        self.assertEqual(0, result)
        result = self.v.validate(
            TestField('f'),
            'f', {})
        self.assertEqual(0, result)

    def test_serializeValue(self):
        handler = FakeSaxHandler()
        value = False
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1)
        self.v.serializeValue(field, value, handler)
        self.assertEqual('False', handler.getXml())
        handler2 = FakeSaxHandler()
        value = True
        self.v.serializeValue(field, value, handler2)
        self.assertEqual('True', handler2.getXml())

    def test_deserializeValue(self):
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1)
        self.assertEqual(
            False,
            self.v.deserializeValue(field, 'False'))
        self.assertEqual(
            True,
            self.v.deserializeValue(field, 'True'))


class IntegerValidatorTestCase(ValidatorTestCase):
    def setUp(self):
        self.v = Validator.IntegerValidatorInstance

    def test_basic(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0, start="", end=""),
            'f', {'f': '15'})
        self.assertEqual(15, result)

        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0, start="", end=""),
            'f', {'f': '0'})
        self.assertEqual(0, result)

        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0, start="", end=""),
            'f', {'f': '-1'})
        self.assertEqual(-1, result)

    def test_no_entry(self):
        # result should be empty string if nothing entered
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0, start="", end=""),
            'f', {'f': ''})
        self.assertEqual("", result)

    def test_ranges(self):
        # first check whether everything that should be in range is
        # in range
        for i in range(0, 100):
            result = self.v.validate(
                TestField('f', max_length=0, truncate=0, required=1,
                          start=0, end=100),
                'f', {'f': str(i)})
            self.assertEqual(i, result)
        # now check out of range errors
        self.assertValidatorRaises(
            Validator.ValidationError, 'integer_out_of_range',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start=0, end=100),
            'f', {'f': '100'})
        self.assertValidatorRaises(
            Validator.ValidationError, 'integer_out_of_range',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start=0, end=100),
            'f', {'f': '200'})
        self.assertValidatorRaises(
            Validator.ValidationError, 'integer_out_of_range',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start=0, end=100),
            'f', {'f': '-10'})
        # check some weird ranges
        self.assertValidatorRaises(
            Validator.ValidationError, 'integer_out_of_range',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start=10, end=10),
            'f', {'f': '10'})
        self.assertValidatorRaises(
            Validator.ValidationError, 'integer_out_of_range',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start=0, end=0),
            'f', {'f': '0'})
        self.assertValidatorRaises(
            Validator.ValidationError, 'integer_out_of_range',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start=0, end=-10),
            'f', {'f': '-1'})

    def test_error_not_integer(self):
        self.assertValidatorRaises(
            Validator.ValidationError, 'not_integer',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start="", end=""),
            'f', {'f': 'foo'})

        self.assertValidatorRaises(
            Validator.ValidationError, 'not_integer',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start="", end=""),
            'f', {'f': '1.0'})

        self.assertValidatorRaises(
            Validator.ValidationError, 'not_integer',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start="", end=""),
            'f', {'f': '1e'})

    def test_error_required_not_found(self):
        # empty string
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start="", end=""),
            'f', {'f': ''})
        # whitespace only
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start="", end=""),
            'f', {'f': '   '})
        # not in dict
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start="", end=""),
            'f', {})

    def test_serializeValue(self):
        handler = FakeSaxHandler()
        value = 1337
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1)
        self.v.serializeValue(field, value, handler)
        self.assertEqual('1337', handler.getXml())

    def test_deserializeValue(self):
        field = TestField(
            'f',
            max_length=0,
            truncate=0,
            required=0,
            unicode=1,
            start=0,
            end=2000)
        self.assertEqual(
            1337,
            self.v.deserializeValue(field, '1337'))


class FloatValidatorTestCase(ValidatorTestCase):
    def setUp(self):
        self.v = Validator.FloatValidatorInstance

    def test_basic(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0),
            'f', {'f': '15.5'})
        self.assertEqual(15.5, result)

        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0),
            'f', {'f': '15.0'})
        self.assertEqual(15.0, result)

        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0),
            'f', {'f': '15'})
        self.assertEqual(15.0, result)

    def test_error_not_float(self):
        self.assertValidatorRaises(
            Validator.ValidationError, 'not_float',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1),
            'f', {'f': '1f'})

    def test_serializeValue(self):
        handler = FakeSaxHandler()
        value = 1.00001
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1)
        self.v.serializeValue(field, value, handler)
        self.assertEqual('1.00001', handler.getXml())

    def test_deserializeValue(self):
        string = '1.00001'
        field = TestField(
            'f',
            max_length=0,
            truncate=0,
            required=0,
            unicode=1,
            start=0,
            end=2000)
        self.assertEqual(
            1.00001,
            self.v.deserializeValue(field, string))


class DateTimeValidatorTestCase(ValidatorTestCase):
    def setUp(self):
        self.v = Validator.DateTimeValidatorInstance

    def test_normal(self):
        result = self.v.validate(
            DateTimeField('f'),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30'})
        self.assertEqual(2002, result.year())
        self.assertEqual(12, result.month())
        self.assertEqual(1, result.day())
        self.assertEqual(10, result.hour())
        self.assertEqual(30, result.minute())

    def test_ampm(self):
        result = self.v.validate(
            DateTimeField('f', ampm_time_style=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30',
                  'subfield_f_ampm': 'am'})
        self.assertEqual(2002, result.year())
        self.assertEqual(12, result.month())
        self.assertEqual(1, result.day())
        self.assertEqual(10, result.hour())
        self.assertEqual(30, result.minute())

        result = self.v.validate(
            DateTimeField('f', ampm_time_style=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30',
                  'subfield_f_ampm': 'pm'})
        self.assertEqual(2002, result.year())
        self.assertEqual(12, result.month())
        self.assertEqual(1, result.day())
        self.assertEqual(22, result.hour())
        self.assertEqual(30, result.minute())

        self.assertValidatorRaises(
            Validator.ValidationError, 'not_datetime',
            self.v.validate,
            DateTimeField('f', ampm_time_style=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30'})

    def test_date_only(self):
        result = self.v.validate(
            DateTimeField('f', date_only=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1'})
        self.assertEqual(2002, result.year())
        self.assertEqual(12, result.month())
        self.assertEqual(1, result.day())
        self.assertEqual(0, result.hour())
        self.assertEqual(0, result.minute())

        result = self.v.validate(
            DateTimeField('f', date_only=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30'})
        self.assertEqual(2002, result.year())
        self.assertEqual(12, result.month())
        self.assertEqual(1, result.day())
        self.assertEqual(0, result.hour())
        self.assertEqual(0, result.minute())

    def test_allow_empty_time(self):
        result = self.v.validate(
            DateTimeField('f', allow_empty_time=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1'})
        self.assertEqual(2002, result.year())
        self.assertEqual(12, result.month())
        self.assertEqual(1, result.day())
        self.assertEqual(0, result.hour())
        self.assertEqual(0, result.minute())

        result = self.v.validate(
            DateTimeField('f', allow_empty_time=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30'})
        self.assertEqual(2002, result.year())
        self.assertEqual(12, result.month())
        self.assertEqual(1, result.day())
        self.assertEqual(10, result.hour())
        self.assertEqual(30, result.minute())

    def test_allow_empty_time2(self):
        result = self.v.validate(
            DateTimeField('f', allow_empty_time=1, required=0), 'f', {})
        self.assertEqual(None, result)

    def test_date_failure(self):
        self.assertValidatorRaises(
            Validator.ValidationError, 'not_datetime',
            self.v.validate,
            DateTimeField('f'),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '6',
                  'subfield_f_day': '35',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30'})

        self.assertValidatorRaises(
            Validator.ValidationError, 'not_datetime',
            self.v.validate,
            DateTimeField('f'),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '1',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '61'})

    def test_serializeValue(self):
        # This test expects that the default timezone is CET.
        handler = FakeSaxHandler()
        value = self.v.validate(
            DateTimeField('f', allow_empty_time=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30'})
        field = DateTimeField('f')
        self.v.serializeValue(field, value, handler)
        self.assertEqual('2002-12-01T09:30:00Z', handler.getXml())

    def test_deserializeValue(self):
        string = '2004-04-23T16:13:40Z'
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1)
        self.assertEqual(
            DateTime('2004-04-23T16:13:40Z'),
            self.v.deserializeValue(field, string))

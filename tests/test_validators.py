import unittest
import ZODB
import OFS.Application
from Products.Formulator import Validator


class TestField:
    def __init__(self, id, **kw):
        self.id = id
        self.kw = kw

    def get_value(self, name):
        return self.kw[name]

    def get_error_message(self, key):
        return "nothing"

    def get_form_encoding(self):
        # XXX fake ... what if installed python does not support utf-8?
        return "utf-8"


class ValidatorTestCase(unittest.TestCase):
    def assertValidatorRaises(self, exception, error_key, f, *args, **kw):
        try:
            apply(f, args, kw)
        except Validator.ValidationError, e:
            if e.error_key != error_key:
                self.fail('Got wrong error. Expected %s received %s' %
                          (error_key, e))
            else:
                return
        self.fail('Expected error %s but no error received.' % error_key)

class StringValidatorTestCase(ValidatorTestCase):
    def setUp(self):
        self.v = Validator.StringValidatorInstance

    def tearDown(self):
        pass
        
    def test_basic(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0),
            'f', {'f' : 'foo'})
        self.assertEqual('foo', result)

    def test_htmlquotes(self):
        # XX test html escaping -- I am not sure if this is really wanted ..
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0),
            'f', {'f' : '<html>'})
        self.assertEqual('&lt;html&gt;', result)

    def test_encoding(self):
        utf8_string = 'M\303\274ller' # this is a M&uuml;ller
        unicode_string = unicode(utf8_string, 'utf-8')
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=1),
            'f', {'f' : utf8_string})
        self.assertEqual(unicode_string, result)

    def test_strip_whitespace(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0),
            'f', {'f' : ' foo  '})
        self.assertEqual('foo', result)

    def test_error_too_long(self):
        self.assertValidatorRaises(
            Validator.ValidationError, 'too_long',
            self.v.validate,
            TestField('f', max_length=10, truncate=0, required=0, unicode=0),
            'f', {'f' : 'this is way too long'})
        
    def test_error_truncate(self):
        result = self.v.validate(
            TestField('f', max_length=10, truncate=1, required=0, unicode=0),
            'f', {'f' : 'this is way too long'})
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
        
class EmailValidatorTestCase(ValidatorTestCase):
     
    def setUp(self):
        self.v = Validator.EmailValidatorInstance
        
    def test_basic(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': 'foo@bar.com'})
        self.assertEquals('foo@bar.com', result)
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': 'm.faassen@vet.uu.nl'})
        self.assertEquals('m.faassen@vet.uu.nl', result) 

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

# skip PatternValidator for now

class BooleanValidatorTestCase(ValidatorTestCase):
    def setUp(self):
        self.v = Validator.BooleanValidatorInstance
        
    def tearDown(self):
        pass

    def test_basic(self):
        result = self.v.validate(
            TestField('f'),
            'f', {'f': ''})
        self.assertEquals(0, result)
        result = self.v.validate(
            TestField('f'),
            'f', {'f': 1})
        self.assertEquals(1, result)
        result = self.v.validate(
            TestField('f'),
            'f', {'f': 0})
        self.assertEquals(0, result)
        result = self.v.validate(
            TestField('f'),
            'f', {})
        self.assertEquals(0, result)

class IntegerValidatorTestCase(ValidatorTestCase):
    def setUp(self):
        self.v = Validator.IntegerValidatorInstance

    def test_basic(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0, start="", end=""),
            'f', {'f': '15'})
        self.assertEquals(15, result)  

        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0, start="", end=""),
            'f', {'f': '0'})
        self.assertEquals(0, result)

        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0, start="", end=""),
            'f', {'f': '-1'})
        self.assertEquals(-1, result)
        
    def test_no_entry(self):
        # result should be empty string if nothing entered
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0, start="", end=""),
            'f', {'f': ''})
        self.assertEquals("", result)

    def test_ranges(self):
        # first check whether everything that should be in range is
        # in range
        for i in range(0, 100):
            result = self.v.validate(
                TestField('f', max_length=0, truncate=0, required=1,
                          start=0, end=100),
                'f', {'f': str(i)})
            self.assertEquals(i, result)
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

def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(StringValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(EmailValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(BooleanValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(IntegerValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(FloatValidatorTestCase, 'test'))
    
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
    
